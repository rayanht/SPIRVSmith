from typing import TYPE_CHECKING

from src import OpCode
from src import Signed
from src import Unsigned
from src.annotations import OpDecorate
from src.enums import Decoration
from src.extension import OpExtInst
from src.operators import BinaryOperatorFuzzMixin
from src.operators import GLSLExtensionOperator
from src.operators import UnaryOperatorFuzzMixin
from src.operators.arithmetic import BinaryArithmeticOperator
from src.operators.arithmetic import UnaryArithmeticOperator
from src.predicates import And
from src.predicates import HasLength
from src.predicates import HasType
from src.predicates import IsMatrixType
from src.predicates import IsOfFloatBaseType
from src.predicates import IsOfSignedIntegerBaseType
from src.predicates import IsOfUnsignedIntegerBaseType
from src.predicates import IsScalarFloat
from src.predicates import IsScalarSignedInteger
from src.predicates import IsVectorType
from src.predicates import Or
from src.types.concrete_types import OpTypeFloat
from src.types.concrete_types import OpTypeInt
from src.types.concrete_types import OpTypeStruct
from src.types.concrete_types import OpTypeVector

if TYPE_CHECKING:
    from src.context import Context


# TODO: investigate, this *might* not be deterministic, disabling it for now
# class Round(UnaryOperatorFuzzMixin, UnaryArithmeticOperator[OpTypeFloat, None, None, None], GLSLExtensionOperator):
#     ...


class RoundEven(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class Trunc(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class FAbs(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class SAbs(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeInt, None, Signed, None],
    GLSLExtensionOperator,
):
    ...


class FSign(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class SSign(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeInt, None, Signed, None],
    GLSLExtensionOperator,
):
    ...


class Floor(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class Ceil(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class Fract(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class Degrees(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class Sin(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class Cos(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class Tan(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class Asin(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class Acos(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class Atan(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class Sinh(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class Cosh(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class Tanh(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class Asinh(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class Acosh(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class Atanh(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class Atan2(
    BinaryOperatorFuzzMixin,
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class Pow(
    BinaryOperatorFuzzMixin,
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class Exp(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class Log(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class Exp2(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class Log2(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class Sqrt(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class InverseSqrt(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class Determinant(
    UnaryArithmeticOperator[None, None, None, None], GLSLExtensionOperator
):
    def fuzz(self, context: "Context") -> list[OpCode]:
        operand = context.get_random_operand(
            lambda x: IsMatrixType(x) and len(x.type) == len(x.type.type)
        )
        if not operand:
            return []
        result_type = operand.get_base_type()
        return [
            OpExtInst(
                type=result_type,
                extension_set=context.extension_sets["GLSL"],
                instruction=self.__class__,
                operands=(operand,),
            )
        ]


# class MatrixInverse(
#     UnaryArithmeticOperator[None, None, None, None], GLSLExtensionOperator
# ):
#     def fuzz(self, context: "Context") -> list[OpCode]:
#         operand = context.get_random_operand(
#             lambda x: IsMatrixType(x) and len(x.type) == len(x.type.type)
#         )
#         return [
#             OpExtInst(
#                 type=operand.type,
#                 extension_set=context.extension_sets["GLSL"],
#                 instruction=self.__class__,
#                 operands=(operand,),
#             )
#         ]


class ModfStruct(
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    def fuzz(self, context: "Context") -> list[OpCode]:
        operand = context.get_random_operand(
            Or(And(IsVectorType, IsOfFloatBaseType), IsScalarFloat)
        )
        if not operand:
            return []
        result_type = OpTypeStruct()
        result_type.types = (operand.type, operand.type)
        context.add_to_tvc(result_type)
        return [
            OpExtInst(
                type=result_type,
                extension_set=context.extension_sets["GLSL"],
                instruction=self.__class__,
                operands=(operand,),
            )
        ]


class FMin(
    BinaryOperatorFuzzMixin,
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class UMin(
    BinaryOperatorFuzzMixin,
    BinaryArithmeticOperator[OpTypeInt, None, Unsigned, None],
    GLSLExtensionOperator,
):
    ...


class SMin(
    BinaryOperatorFuzzMixin,
    BinaryArithmeticOperator[OpTypeInt, None, Signed, None],
    GLSLExtensionOperator,
):
    ...


class FMax(
    BinaryOperatorFuzzMixin,
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class UMax(
    BinaryOperatorFuzzMixin,
    BinaryArithmeticOperator[OpTypeInt, None, Unsigned, None],
    GLSLExtensionOperator,
):
    ...


class SMax(
    BinaryOperatorFuzzMixin,
    BinaryArithmeticOperator[OpTypeInt, None, Signed, None],
    GLSLExtensionOperator,
):
    ...


# TODO: we need a ternary arithmetic operator classification, workaround for now
class FClamp(
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    def fuzz(self, context: "Context") -> list[OpCode]:
        operand1 = context.get_random_operand(
            Or(And(IsVectorType, IsOfFloatBaseType), IsScalarFloat)
        )
        if not operand1:
            return []
        operand2 = context.get_random_operand(HasType(operand1.type))
        operand3 = context.get_random_operand(HasType(operand1.type))
        return [
            OpExtInst(
                type=operand1.type,
                extension_set=context.extension_sets["GLSL"],
                instruction=self.__class__,
                operands=(operand1, operand2, operand3),
            )
        ]


class UClamp(
    BinaryArithmeticOperator[OpTypeInt, None, Unsigned, None],
    GLSLExtensionOperator,
):
    def fuzz(self, context: "Context") -> list[OpCode]:
        operand1 = context.get_random_operand(
            Or(And(IsVectorType, IsOfUnsignedIntegerBaseType), IsScalarSignedInteger)
        )
        if not operand1:
            return []
        operand2 = context.get_random_operand(HasType(operand1.type))
        operand3 = context.get_random_operand(HasType(operand1.type))
        return [
            OpExtInst(
                type=operand1.type,
                extension_set=context.extension_sets["GLSL"],
                instruction=self.__class__,
                operands=(operand1, operand2, operand3),
            )
        ]


class SClamp(
    BinaryArithmeticOperator[OpTypeInt, None, Signed, None],
    GLSLExtensionOperator,
):
    def fuzz(self, context: "Context") -> list[OpCode]:
        operand1 = context.get_random_operand(
            Or(And(IsVectorType, IsOfSignedIntegerBaseType), IsScalarSignedInteger)
        )
        if not operand1:
            return []
        operand2 = context.get_random_operand(HasType(operand1.type))
        operand3 = context.get_random_operand(HasType(operand1.type))
        return [
            OpExtInst(
                type=operand1.type,
                extension_set=context.extension_sets["GLSL"],
                instruction=self.__class__,
                operands=(operand1, operand2, operand3),
            )
        ]


class FMix(
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    def fuzz(self, context: "Context") -> list[OpCode]:
        operand1 = context.get_random_operand(
            Or(And(IsVectorType, IsOfFloatBaseType), IsScalarFloat)
        )
        if not operand1:
            return []
        operand2 = context.get_random_operand(HasType(operand1.type))
        operand3 = context.get_random_operand(HasType(operand1.type))
        return [
            OpExtInst(
                type=operand1.type,
                extension_set=context.extension_sets["GLSL"],
                instruction=self.__class__,
                operands=(operand1, operand2, operand3),
            )
        ]


class Step(
    BinaryOperatorFuzzMixin,
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


# class SmoothStep(
#     BinaryArithmeticOperator[OpTypeFloat, None, None, None],
#     GLSLExtensionOperator,
# ):
#     def fuzz(self, context: "Context") -> list[OpCode]:
#         operand1 = context.get_random_operand(
#             Or(And(IsVectorType, IsOfFloatBaseType), IsScalarFloat)
#         )
#         if not operand1:
#             return []
#         operand2 = context.get_random_operand(HasType(operand1.type))
#         operand3 = context.get_random_operand(HasType(operand1.type))
#         return [
#             OpExtInst(
#                 type=operand1.type,
#                 extension_set=context.extension_sets["GLSL"],
#                 instruction=self.__class__,
#                 operands=(operand1, operand2, operand3),
#             )
#         ]


class Fma(
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    def fuzz(self, context: "Context") -> list[OpCode]:
        operand1 = context.get_random_operand(
            Or(And(IsVectorType, IsOfFloatBaseType), IsScalarFloat)
        )
        if not operand1:
            return []
        operand2 = context.get_random_operand(HasType(operand1.type))
        operand3 = context.get_random_operand(HasType(operand1.type))
        ext_inst = OpExtInst(
            type=operand1.type,
            extension_set=context.extension_sets["GLSL"],
            instruction=self.__class__,
            operands=(operand1, operand2, operand3),
        )
        # Required for determinism
        context.add_annotation(
            OpDecorate(target=ext_inst, decoration=Decoration.NoContraction)
        )
        return [ext_inst]


class FrexpStruct(
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    def fuzz(self, context: "Context") -> list[OpCode]:
        operand = context.get_random_operand(
            Or(And(IsVectorType, IsOfFloatBaseType), IsScalarFloat)
        )
        if not operand:
            return []
        struct_type = OpTypeStruct()
        inner_type1 = operand.type
        int_type = OpTypeInt()
        int_type.width = 32
        int_type.signed = 1
        if IsVectorType(operand):
            inner_type2 = OpTypeVector()
            inner_type2.type = int_type
            inner_type2.size = len(inner_type1)
        else:
            inner_type2 = int_type
        context.add_to_tvc(inner_type2)
        struct_type.types = (inner_type1, inner_type2)
        context.add_to_tvc(struct_type)
        return [
            OpExtInst(
                type=struct_type,
                extension_set=context.extension_sets["GLSL"],
                instruction=self.__class__,
                operands=(operand,),
            )
        ]


# # # # # # # # # # # # # # # #
# TODO: packing and unpacking #
# # # # # # # # # # # # # # # #


# # # # # # # # # # # # # # # #


class Length(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    def fuzz(self, context: "Context") -> list[OpCode]:
        operand = context.get_random_operand(And(IsVectorType, IsOfFloatBaseType))
        if not operand:
            return []
        result_type = OpTypeFloat().fuzz(context)[-1]
        return [
            OpExtInst(
                type=result_type,
                extension_set=context.extension_sets["GLSL"],
                instruction=self.__class__,
                operands=(operand,),
            )
        ]


class Distance(
    BinaryOperatorFuzzMixin,
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    def fuzz(self, context: "Context") -> list[OpCode]:
        operand1 = context.get_random_operand(And(IsVectorType, IsOfFloatBaseType))
        if not operand1:
            return []
        operand2 = context.get_random_operand(HasType(operand1.type))
        result_type = OpTypeFloat().fuzz(context)[-1]
        return [
            OpExtInst(
                type=result_type,
                extension_set=context.extension_sets["GLSL"],
                instruction=self.__class__,
                operands=(
                    operand1,
                    operand2,
                ),
            )
        ]


class Cross(
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    def fuzz(self, context: "Context") -> list[OpCode]:
        operand1 = context.get_random_operand(
            And(IsVectorType, IsOfFloatBaseType, HasLength(3))
        )
        if not operand1:
            return []
        operand2 = context.get_random_operand(HasType(operand1.type))
        return [
            OpExtInst(
                type=operand1.type,
                extension_set=context.extension_sets["GLSL"],
                instruction=self.__class__,
                operands=(operand1, operand2),
            )
        ]


class Normalize(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class FaceForward(
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    def fuzz(self, context: "Context") -> list[OpCode]:
        operand1 = context.get_random_operand(
            Or(And(IsVectorType, IsOfFloatBaseType), IsScalarFloat)
        )
        operand2 = context.get_random_operand(HasType(operand1.type))
        operand3 = context.get_random_operand(HasType(operand1.type))
        return [
            OpExtInst(
                type=operand1.type,
                extension_set=context.extension_sets["GLSL"],
                instruction=self.__class__,
                operands=(operand1, operand2, operand3),
            )
        ]


class Reflect(
    BinaryOperatorFuzzMixin,
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


# # TODO
# class Refract:
#     ...


class FindILsb(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeInt, None, None, None],
    GLSLExtensionOperator,
):
    ...


class FindSMsb(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeInt, None, Signed, None],
    GLSLExtensionOperator,
):
    ...


class FindUMsb(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeInt, None, Unsigned, None],
    GLSLExtensionOperator,
):
    ...


# Fragment only
# class InterpolateAtCentroid(
#     UnaryOperatorFuzzMixin,
#     UnaryArithmeticOperator[OpTypeFloat, None, None, None],
#     GLSLExtensionOperator,
# ):
#     ...

# Fragment only
# class InterpolateAtSample(
#     BinaryOperatorFuzzMixin,
#     BinaryArithmeticOperator[OpTypeFloat, None, None, None],
#     GLSLExtensionOperator,
# ):
#     ...

# Fragment only
# class InterpolateAtOffset(
#     BinaryOperatorFuzzMixin,
#     BinaryArithmeticOperator[OpTypeFloat, None, None, None],
#     GLSLExtensionOperator,
# ):
#     ...


class NMin(
    BinaryOperatorFuzzMixin,
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class NMax(
    BinaryOperatorFuzzMixin,
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class NClamp(
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    def fuzz(self, context: "Context") -> list[OpCode]:
        operand1 = context.get_random_operand(
            Or(And(IsVectorType, IsOfFloatBaseType), IsScalarFloat)
        )
        if not operand1:
            return []
        operand2 = context.get_random_operand(HasType(operand1.type))
        operand3 = context.get_random_operand(HasType(operand1.type))
        return [
            OpExtInst(
                type=operand1.type,
                extension_set=context.extension_sets["GLSL"],
                instruction=self.__class__,
                operands=(operand1, operand2, operand3),
            )
        ]
