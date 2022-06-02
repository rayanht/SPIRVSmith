from abc import ABC
from inspect import isclass
from typing import Generic
from typing import TypeAlias
from typing import TypeVar

from src import OpCode
from src.context import Context
from src.extension import OpExtInst
from src.extension import OpExtInstImport
from src.misc import OpUndef
from src.operators.arithmetic.glsl import Acos
from src.operators.arithmetic.glsl import Acosh
from src.operators.arithmetic.glsl import Asin
from src.operators.arithmetic.glsl import Atan2
from src.operators.arithmetic.glsl import Atanh
from src.operators.arithmetic.glsl import FAbs
from src.operators.arithmetic.glsl import FClamp
from src.operators.arithmetic.glsl import FMax
from src.operators.arithmetic.glsl import FMin
from src.operators.arithmetic.glsl import Fract
from src.operators.arithmetic.glsl import InverseSqrt
from src.operators.arithmetic.glsl import Log
from src.operators.arithmetic.glsl import Log2
from src.operators.arithmetic.glsl import NClamp
from src.operators.arithmetic.glsl import NMax
from src.operators.arithmetic.glsl import NMin
from src.operators.arithmetic.glsl import Pow
from src.operators.arithmetic.glsl import SAbs
from src.operators.arithmetic.glsl import SClamp
from src.operators.arithmetic.glsl import SMax
from src.operators.arithmetic.glsl import SMin
from src.operators.arithmetic.glsl import Sqrt
from src.operators.arithmetic.glsl import UClamp
from src.operators.arithmetic.glsl import UMax
from src.operators.arithmetic.glsl import UMin
from src.operators.arithmetic.scalar_arithmetic import OpFAdd
from src.operators.arithmetic.scalar_arithmetic import OpFMod
from src.operators.arithmetic.scalar_arithmetic import OpFRem
from src.operators.arithmetic.scalar_arithmetic import OpFSub
from src.operators.arithmetic.scalar_arithmetic import OpIAdd
from src.operators.arithmetic.scalar_arithmetic import OpISub
from src.operators.arithmetic.scalar_arithmetic import OpSDiv
from src.operators.arithmetic.scalar_arithmetic import OpSMod
from src.operators.arithmetic.scalar_arithmetic import OpSRem
from src.operators.arithmetic.scalar_arithmetic import OpUDiv
from src.operators.arithmetic.scalar_arithmetic import OpUMod
from src.operators.bitwise import (
    OpShiftLeftLogical,
)  # OpBitFieldInsert,; OpBitFieldSExtract,; OpBitFieldUExtract,
from src.operators.bitwise import OpShiftRightArithmetic
from src.operators.bitwise import OpShiftRightLogical
from src.operators.composite import OpVectorExtractDynamic
from src.operators.composite import OpVectorInsertDynamic
from src.predicates import IsOfFloatBaseType
from src.predicates import IsVectorType
from src.types.concrete_types import OpTypeFloat
from src.types.concrete_types import OpTypeInt

T = TypeVar("T")


class DangerousPattern(ABC, Generic[T]):
    @staticmethod
    def recondition(context: Context, opcode: T):
        ...

    @staticmethod
    def get_affected_opcodes() -> set[T]:
        ...


UndefOpCodeVulnerableOpCode: TypeAlias = OpCode


class UndefOpCode(DangerousPattern[UndefOpCodeVulnerableOpCode]):
    @staticmethod
    def recondition(
        context: Context,
        opcode: UndefOpCodeVulnerableOpCode,
    ):
        if not isclass(opcode):
            fuzzed_opcode = None
            for attr in opcode.members():
                if attr.startswith("type") or attr.endswith("type"):
                    continue
                if isinstance(getattr(opcode, attr), OpUndef):
                    fuzzed_opcode = opcode.fuzz(context).opcode
                    for attr in opcode.members():
                        setattr(opcode, attr, getattr(fuzzed_opcode, attr))
                    break
        return []

    @staticmethod
    def get_affected_opcodes() -> set[type[UndefOpCodeVulnerableOpCode]]:
        return {OpCode}


VectorAccessOutOfBoundsVulnerableOpCode: TypeAlias = (
    OpVectorExtractDynamic | OpVectorInsertDynamic
)


class VectorAccessOutOfBounds(
    DangerousPattern[VectorAccessOutOfBoundsVulnerableOpCode]
):
    @staticmethod
    def recondition(context: Context, opcode: VectorAccessOutOfBoundsVulnerableOpCode):
        """Recondition vector accesses using a modulo operation."""
        operand1 = opcode.index
        index_type = opcode.index.type
        operand2 = context.create_on_demand_numerical_constant(
            index_type.__class__,
            value=len(opcode.vector.type),
            width=index_type.width,
            signed=index_type.signed,
        )

        if index_type.signed:
            op_mod = OpSMod(index_type, operand1, operand2)
        else:
            op_mod = OpUMod(index_type, operand1, operand2)
        opcode.index = op_mod
        return [op_mod]

    @staticmethod
    def get_affected_opcodes() -> set[type[VectorAccessOutOfBoundsVulnerableOpCode]]:
        return {OpVectorExtractDynamic, OpVectorInsertDynamic}


TooLargeMagnitudeVulnerableOpCode: TypeAlias = Asin | Acos | Atanh


class TooLargeMagnitude(DangerousPattern[TooLargeMagnitudeVulnerableOpCode]):
    @staticmethod
    def recondition(
        context: Context,
        opcode: TooLargeMagnitudeVulnerableOpCode,
    ):
        """Recondition |x| > 1 scalars using x := x - floor(x)."""
        op_fract = OpExtInst(
            type=opcode.operand1.type,
            extension_set=context.extension_sets["GLSL.std.450"],
            instruction=Fract,
            operands=(opcode.operand1,),
        )
        opcode.operand1 = op_fract
        return [op_fract]

    @staticmethod
    def get_affected_opcodes() -> set[type[TooLargeMagnitudeVulnerableOpCode]]:
        return {Asin, Acos, Atanh}


FirstOperandLessThanOneVulnerableOpCode: TypeAlias = (
    Acosh | Log | Pow | Log2 | Sqrt | InverseSqrt
)


class FirstOperandLessThanOne(
    DangerousPattern[FirstOperandLessThanOneVulnerableOpCode]
):
    @staticmethod
    def recondition(
        context: Context,
        opcode: FirstOperandLessThanOneVulnerableOpCode,
    ):
        """Recondition x < 1 scalars using x := |x| + 1"""
        # Operands will always be floats
        op_abs = OpExtInst(
            type=opcode.operand1.type,
            extension_set=context.extension_sets["GLSL.std.450"],
            instruction=FAbs,
            operands=(opcode.operand1,),
        )
        const_one = context.create_on_demand_numerical_constant(OpTypeFloat, value=1.0)
        if IsVectorType(opcode.operand1):
            const_one = context.create_on_demand_vector_constant(
                inner_constant=const_one, size=len(opcode.operand1.type)
            )
        op_add = OpFAdd(opcode.operand1.type, op_abs, const_one)
        opcode.operand1 = op_add
        return [op_abs, op_add]

    @staticmethod
    def get_affected_opcodes() -> set[type[FirstOperandLessThanOneVulnerableOpCode]]:
        return {Acosh, Log, Pow, Log2, Sqrt, InverseSqrt}


SecondOperandEqualsZeroVulnerableOpCode: TypeAlias = (
    OpUMod | OpSMod | OpSRem | OpFRem | OpFMod | OpSDiv | OpUDiv
)


class SecondOperandEqualsZero(
    DangerousPattern[SecondOperandEqualsZeroVulnerableOpCode]
):
    @staticmethod
    def recondition(
        context: Context,
        opcode: SecondOperandEqualsZeroVulnerableOpCode,
    ):
        """Recondition op(x, y) AND y = 0 using y := |y| + 1"""
        match opcode.operand2.get_base_type():
            case OpTypeFloat():
                op_abs: OpExtInst = OpExtInst(
                    type=opcode.operand2.type,
                    extension_set=context.extension_sets["GLSL.std.450"],
                    instruction=FAbs,
                    operands=(opcode.operand2,),
                )
            case OpTypeInt(signed=1):
                op_abs: OpExtInst = OpExtInst(
                    type=opcode.operand2.type,
                    extension_set=context.extension_sets["GLSL.std.450"],
                    instruction=SAbs,
                    operands=(opcode.operand2,),
                )
            case OpTypeInt(signed=0):
                op_abs = None
        const_one = context.create_on_demand_numerical_constant(
            opcode.operand2.get_base_type().__class__, value=1
        )
        if IsVectorType(opcode.operand2):
            const_one = context.create_on_demand_vector_constant(
                inner_constant=const_one, size=len(opcode.operand2.type)
            )
        match opcode.operand2.get_base_type():
            case OpTypeFloat():
                op_add: OpFAdd = OpFAdd(
                    opcode.operand2.type,
                    op_abs if op_abs else opcode.operand2,
                    const_one,
                )
            case OpTypeInt():
                op_add: OpIAdd = OpIAdd(
                    opcode.operand2.type,
                    op_abs if op_abs else opcode.operand2,
                    const_one,
                )
        opcode.operand2 = op_add
        if op_abs:
            return [op_abs, op_add]
        return [op_add]

    @staticmethod
    def get_affected_opcodes() -> set[type[SecondOperandEqualsZeroVulnerableOpCode]]:
        return {OpUMod, OpSMod, OpSRem, OpFRem, OpFMod, OpSDiv, OpUDiv}


BothOperandsEqualZeroVulnerableOpCode: TypeAlias = Atan2


class BothOperandsEqualZero(DangerousPattern[BothOperandsEqualZeroVulnerableOpCode]):
    @staticmethod
    def recondition(
        context: Context,
        opcode: BothOperandsEqualZeroVulnerableOpCode,
    ):
        """Recondition x == y == 0
        x := x - y + 1
        y := y - x + 1
        """
        operand_base_type = opcode.operand1.get_base_type()
        if IsOfFloatBaseType(operand_base_type):
            add = OpFAdd
            sub = OpFSub
            signedness = None
        else:
            add = OpIAdd
            sub = OpISub
            signedness = operand_base_type.signed
        const_one = context.create_on_demand_numerical_constant(
            operand_base_type.__class__, value=1, signed=signedness
        )
        if IsVectorType(opcode.operand1):
            const_one = context.create_on_demand_vector_constant(
                inner_constant=const_one, size=len(opcode.operand1.type)
            )
        op_sub1 = sub(opcode.operand1.type, opcode.operand1, opcode.operand2)
        op_add1 = add(opcode.operand1.type, op_sub1, const_one)

        op_sub2 = sub(opcode.operand2.type, opcode.operand2, opcode.operand1)
        op_add2 = add(opcode.operand2.type, op_sub2, const_one)

        opcode.operand1 = op_add1
        opcode.operand2 = op_add2
        return [op_sub1, op_add1, op_sub2, op_add2]

    @staticmethod
    def get_affected_opcodes() -> set[type[BothOperandsEqualZeroVulnerableOpCode]]:
        return {Atan2}


DegenerateClampVulnerableOpCode: TypeAlias = FClamp | UClamp | SClamp | NClamp


class DegenerateClamp(DangerousPattern[DegenerateClampVulnerableOpCode]):
    @staticmethod
    def recondition(
        context: Context,
        opcode: DegenerateClampVulnerableOpCode,
    ):
        """Recondition clamp(x, minVal, maxVal)
        minVal := min(minVal, maxVal)
        maxVal := max(minVal, maxVal)
        """
        match opcode.__name__:
            case "FClamp":
                op_min = FMin
                op_max = FMax
            case "UClamp":
                op_min = UMin
                op_max = UMax
            case "SClamp":
                op_min = SMin
                op_max = SMax
            case "NClamp":
                op_min = NMin
                op_max = NMax
        op_min = OpExtInst(
            type=opcode.operand2.type,
            extension_set=context.extension_sets["GLSL.std.450"],
            instruction=op_min,
            operands=(opcode.operand2, opcode.operand3),
        )
        op_max = OpExtInst(
            type=opcode.operand2.type,
            extension_set=context.extension_sets["GLSL.std.450"],
            instruction=op_max,
            operands=(opcode.operand2, opcode.operand3),
        )
        opcode.operand2 = op_min
        opcode.operand3 = op_max
        return [op_min, op_max]

    @staticmethod
    def get_affected_opcodes() -> set[type[DegenerateClampVulnerableOpCode]]:
        return {FClamp, UClamp, SClamp, NClamp}


TooLargeShiftVulnerableOpCode: TypeAlias = (
    OpShiftLeftLogical | OpShiftRightLogical | OpShiftRightArithmetic
)


class TooLargeShift(DangerousPattern[TooLargeShiftVulnerableOpCode]):
    @staticmethod
    def recondition(
        context: Context,
        opcode: TooLargeShiftVulnerableOpCode,
    ):
        """Recondition shift(x, y)
        y := |y| % sizeof(base_type(x))
        """
        base_type = opcode.operand2.get_base_type()
        const = context.create_on_demand_numerical_constant(
            base_type.__class__,
            value=base_type.width,
            width=base_type.width,
            signed=base_type.signed,
        )
        op_abs = None
        if base_type.signed:
            # TODO the Abs shouldn't be necessary but SPIRV-Cross generates undefined MSL otherwise.
            # See https://github.com/KhronosGroup/SPIRV-Cross/issues/1933
            op_abs = OpExtInst(
                type=opcode.operand2.type,
                extension_set=context.extension_sets["GLSL.std.450"],
                instruction=SAbs,
                operands=(opcode.operand2,),
            )
            op_mod = OpSMod(opcode.operand2.type, op_abs, const)
        else:
            op_mod = OpUMod(opcode.operand2.type, opcode.operand2, const)
        if IsVectorType(opcode.operand1):
            op_mod.operand2 = context.create_on_demand_vector_constant(
                inner_constant=op_mod.operand2, size=len(opcode.operand1.type)
            )
        opcode.operand2 = op_mod
        if op_abs:
            return [op_abs, op_mod]
        return [op_mod]

    @staticmethod
    def get_affected_opcodes() -> set[type[TooLargeShiftVulnerableOpCode]]:
        return {OpShiftLeftLogical, OpShiftRightLogical, OpShiftRightArithmetic}


# DegenerateBitManipulationVulnerableOpCode: TypeAlias = (
#     OpBitFieldInsert | OpBitFieldSExtract | OpBitFieldUExtract
# )


# class DegenerateBitManipulation(
#     DangerousPattern[DegenerateBitManipulationVulnerableOpCode]
# ):
#     @staticmethod
#     def generate_clamp(context: Context, operand, lower_bound: int, upper_bound: int):
#         const_lower = context.create_on_demand_numerical_constant(
#             operand.get_base_type().__class__,
#             lower_bound,
#             operand.get_base_type().width,
#             operand.get_base_type().signed,
#         )
#         const_upper = context.create_on_demand_numerical_constant(
#             operand.get_base_type().__class__,
#             upper_bound,
#             operand.get_base_type().width,
#             operand.get_base_type().signed,
#         )
#         if operand.get_base_type().signed:
#             return OpExtInst(
#                 type=operand.type,
#                 extension_set=context.extension_sets["GLSL.std.450"],
#                 instruction=SClamp,
#                 operands=(operand, const_lower, const_upper),
#             )
#         return OpExtInst(
#             type=operand.type,
#             extension_set=context.extension_sets["GLSL.std.450"],
#             instruction=UClamp,
#             operands=(operand, const_lower, const_upper),
#         )

#     @staticmethod
#     def recondition(
#         context: Context,
#         opcode: DegenerateBitManipulationVulnerableOpCode,
#     ):
#         opcode.offset = DegenerateBitManipulation.generate_clamp(context, opcode.offset, 0, 16)
#         opcode.count = DegenerateBitManipulation.generate_clamp(context, opcode.count, 0, 16)
#         return [opcode.offset, opcode.count]

#     @staticmethod
#     def get_affected_opcodes() -> set[type[DegenerateClampVulnerableOpCode]]:
#         return {OpBitFieldInsert, OpBitFieldSExtract, OpBitFieldUExtract}


def recondition_opcodes(context: Context, spirv_opcodes: list[OpCode]):
    dangerous_patterns = DangerousPattern.__subclasses__()
    i = 0
    j = len(spirv_opcodes)
    reconditioning_side_effects = []
    if "GLSL.std.450" not in context.extension_sets:
        context.extension_sets["GLSL.std.450"] = OpExtInstImport("GLSL.std.450")
    while i < j:
        opcode = spirv_opcodes[i]
        for dangerous_pattern in dangerous_patterns:
            if isinstance(opcode, OpExtInst):
                opcode_class = opcode.instruction
                for k in range(len((opcode.operands))):
                    setattr(opcode.instruction, f"operand{k + 1}", opcode.operands[k])
            else:
                opcode_class = opcode.__class__
            if any(
                [
                    issubclass(opcode_class, affected_opcode)
                    for affected_opcode in dangerous_pattern.get_affected_opcodes()
                ]
            ):
                reconditioning_side_effects = dangerous_pattern.recondition(
                    context,
                    opcode.instruction if isinstance(opcode, OpExtInst) else opcode,
                )
                spirv_opcodes = (
                    spirv_opcodes[:i] + reconditioning_side_effects + spirv_opcodes[i:]
                )
                i += len(reconditioning_side_effects)
                # Reset the OpExtInst and update operands
                if isinstance(opcode, OpExtInst):
                    opcode.operands = tuple(
                        list(
                            filter(
                                None,
                                [
                                    getattr(opcode.instruction, "operand1", None),
                                    getattr(opcode.instruction, "operand2", None),
                                    getattr(opcode.instruction, "operand3", None),
                                ],
                            )
                        )
                    )
                    opcode.instruction = opcode_class
        i += 1
        j = len(spirv_opcodes)
    return spirv_opcodes
