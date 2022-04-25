from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import TypeVar

from src import OpCode
from src.context import Context
from src.extension import OpExtInst
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
from src.operators.arithmetic.glsl import SClamp
from src.operators.arithmetic.glsl import SMax
from src.operators.arithmetic.glsl import SMin
from src.operators.arithmetic.glsl import Sqrt
from src.operators.arithmetic.glsl import UClamp
from src.operators.arithmetic.glsl import UMax
from src.operators.arithmetic.glsl import UMin
from src.operators.arithmetic.scalar_arithmetic import OpFAdd
from src.operators.arithmetic.scalar_arithmetic import OpFSub
from src.operators.arithmetic.scalar_arithmetic import OpIAdd
from src.operators.arithmetic.scalar_arithmetic import OpISub
from src.operators.arithmetic.scalar_arithmetic import OpSMod
from src.operators.arithmetic.scalar_arithmetic import OpUMod
from src.operators.composite import OpVectorExtractDynamic
from src.operators.composite import OpVectorInsertDynamic
from src.predicates import IsBaseTypeSigned
from src.predicates import IsOfFloatBaseType
from src.predicates import IsVectorType
from src.types.concrete_types import OpTypeFloat

T = TypeVar("T")


class DangerousPattern(ABC, Generic[T]):
    @abstractmethod
    def recondition(self, context: Context, opcode: T):
        ...

    @abstractmethod
    def get_affected_opcodes(self) -> set[T]:
        ...


VectorAccessOutOfBoundsVulnerableOpCode = OpVectorExtractDynamic | OpVectorInsertDynamic


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
            mod = OpSMod
        else:
            mod = OpUMod
        op_mod = mod()
        op_mod.type = index_type
        op_mod.operand1 = operand1
        op_mod.operand2 = operand2
        opcode.index = op_mod
        return [op_mod]

    @staticmethod
    def get_affected_opcodes() -> set[VectorAccessOutOfBoundsVulnerableOpCode]:
        return {OpVectorExtractDynamic, OpVectorInsertDynamic}


FirstOperandAbsLessThanOneeVulnerableOpCode = Asin | Acos | Atanh


class TooLargeMagnitude(DangerousPattern[FirstOperandAbsLessThanOneeVulnerableOpCode]):
    @staticmethod
    def recondition(
        context: Context,
        opcode: FirstOperandAbsLessThanOneeVulnerableOpCode,
    ):
        """Recondition |x| > 1 scalars using x := x - floor(x)."""
        op_fract = OpExtInst(
            type=opcode.operand1.type,
            extension_set=context.extension_sets["GLSL"],
            instruction=Fract,
            operands=[opcode.operand1],
        )
        opcode.operand1 = op_fract
        return [op_fract]

    @staticmethod
    def get_affected_opcodes() -> set[FirstOperandAbsLessThanOneeVulnerableOpCode]:
        return {Asin, Acos, Atanh}


FirstOperandLessThanOneVulnerableOpCode = Acosh | Log | Pow | Log2 | Sqrt | InverseSqrt


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
            extension_set=context.extension_sets["GLSL"],
            instruction=FAbs,
            operands=[opcode.operand1],
        )
        const_one = context.create_on_demand_numerical_constant(OpTypeFloat, value=1.0)
        if IsVectorType(opcode.operand1):
            const_one = context.create_on_demand_vector_constant(
                inner_constant=const_one, size=len(opcode.operand1.type)
            )
        op_add = OpFAdd()
        op_add.type = opcode.operand1.type
        op_add.operand1 = op_abs
        op_add.operand2 = const_one
        opcode.operand1 = op_add
        return [op_abs, op_add]

    @staticmethod
    def get_affected_opcodes() -> set[FirstOperandLessThanOneVulnerableOpCode]:
        return {Acosh, Log, Pow, Log2, Sqrt, InverseSqrt}


BothOperandsEqualZeroVulnerableOpCode = Atan2


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
        op_sub1 = sub()
        op_sub1.type = opcode.operand1.type
        op_sub1.operand1 = opcode.operand1
        op_sub1.operand2 = opcode.operand2
        op_add1 = add()
        op_add1.type = opcode.operand1.type
        op_add1.operand1 = op_sub1
        op_add1.operand2 = const_one

        op_sub2 = sub()
        op_sub2.type = opcode.operand2.type
        op_sub2.operand1 = opcode.operand2
        op_sub2.operand2 = opcode.operand1
        op_add2 = add()
        op_add2.type = opcode.operand2.type
        op_add2.operand1 = op_sub2
        op_add2.operand2 = const_one

        opcode.operand1 = op_add1
        opcode.operand2 = op_add2
        return [op_sub1, op_add1, op_sub2, op_add2]

    @staticmethod
    def get_affected_opcodes() -> set[BothOperandsEqualZeroVulnerableOpCode]:
        return {Atan2}


DegenerateClampVulnerableOpCode = FClamp | UClamp | SClamp | NClamp


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
                op_min = FMin()
                op_max = FMax()
            case "UClamp":
                op_min = UMin()
                op_max = UMax()
            case "SClamp":
                op_min = SMin()
                op_max = SMax()
            case "NClamp":
                op_min = NMin()
                op_max = NMax()
        op_min = OpExtInst(
            type=opcode.operand2.type,
            extension_set=context.extension_sets["GLSL"],
            instruction=op_min.__class__,
            operands=[opcode.operand2, opcode.operand3],
        )
        op_max = OpExtInst(
            type=opcode.operand2.type,
            extension_set=context.extension_sets["GLSL"],
            instruction=op_max.__class__,
            operands=[opcode.operand2, opcode.operand3],
        )
        opcode.operand2 = op_min
        opcode.operand3 = op_max
        return [op_min, op_max]

    @staticmethod
    def get_affected_opcodes() -> set[DegenerateClampVulnerableOpCode]:
        return {FClamp, UClamp, SClamp, NClamp}


def recondition(context: Context, spirv_opcodes: list[OpCode]):
    dangerous_patterns = DangerousPattern.__subclasses__()
    i = 0
    j = len(spirv_opcodes)
    reconditioning_side_effects = []
    while i < j:
        opcode = spirv_opcodes[i]
        for dangerous_pattern in dangerous_patterns:
            if isinstance(opcode, OpExtInst):
                opcode_class = opcode.instruction
                for k in range(len((opcode.operands))):
                    setattr(opcode.instruction, f"operand{k + 1}", opcode.operands[k])
            else:
                opcode_class = opcode.__class__
            if opcode_class in dangerous_pattern.get_affected_opcodes():
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
