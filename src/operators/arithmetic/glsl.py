from typing import TYPE_CHECKING

from typing_extensions import Self

from src import FuzzResult
from src import Signed
from src import Unsigned
from src.extension import OpExtInst
from src.operators import BinaryOperatorFuzzMixin
from src.operators import GLSLExtensionOperator
from src.operators import UnaryOperatorFuzzMixin
from src.operators.arithmetic import BinaryArithmeticOperator
from src.operators.arithmetic import UnaryArithmeticOperator
from src.patched_dataclass import dataclass
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


@dataclass
class RoundEven(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class Trunc(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class FAbs(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class SAbs(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeInt, None, Signed, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class FSign(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class SSign(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeInt, None, Signed, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class Floor(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class Ceil(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class Fract(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class Degrees(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class Sin(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class Cos(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class Tan(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class Asin(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class Acos(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class Atan(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class Sinh(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class Cosh(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class Tanh(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class Asinh(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class Acosh(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class Atanh(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class Atan2(
    BinaryOperatorFuzzMixin,
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class Pow(
    BinaryOperatorFuzzMixin,
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class Exp(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class Log(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class Exp2(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class Log2(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class Sqrt(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class InverseSqrt(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class Determinant(
    UnaryArithmeticOperator[None, None, None, None], GLSLExtensionOperator
):
    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        operand = context.get_random_operand(
            lambda x: IsMatrixType(x) and len(x.type) == len(x.type.type)
        )
        result_type = operand.get_base_type()
        return FuzzResult(
            OpExtInst(
                type=result_type,
                extension_set=context.extension_sets["GLSL.std.450"],
                instruction=cls,
                operands=(operand,),
            ),
            [result_type],
        )


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
#                 extension_set=context.extension_sets["GLSL.std.450"],
#                 instruction=self.__class__,
#                 operands=(operand,),
#             )
#         ]


@dataclass
class ModfStruct(
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        operand = context.get_random_operand(
            Or(And(IsVectorType, IsOfFloatBaseType), IsScalarFloat)
        )
        result_type = OpTypeStruct(types=(operand.type, operand.type))
        return FuzzResult(
            OpExtInst(
                type=result_type,
                extension_set=context.extension_sets["GLSL.std.450"],
                instruction=cls,
                operands=(operand,),
            ),
            [result_type],
        )


@dataclass
class FMin(
    BinaryOperatorFuzzMixin,
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class UMin(
    BinaryOperatorFuzzMixin,
    BinaryArithmeticOperator[OpTypeInt, None, Unsigned, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class SMin(
    BinaryOperatorFuzzMixin,
    BinaryArithmeticOperator[OpTypeInt, None, Signed, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class FMax(
    BinaryOperatorFuzzMixin,
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class UMax(
    BinaryOperatorFuzzMixin,
    BinaryArithmeticOperator[OpTypeInt, None, Unsigned, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class SMax(
    BinaryOperatorFuzzMixin,
    BinaryArithmeticOperator[OpTypeInt, None, Signed, None],
    GLSLExtensionOperator,
):
    ...


# TODO: we need a ternary arithmetic operator classification, workaround for now
@dataclass
class FClamp(
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        operand1 = context.get_random_operand(
            Or(And(IsVectorType, IsOfFloatBaseType), IsScalarFloat)
        )
        operand2 = context.get_random_operand(HasType(operand1.type))
        operand3 = context.get_random_operand(HasType(operand1.type))
        return FuzzResult(
            OpExtInst(
                type=operand1.type,
                extension_set=context.extension_sets["GLSL.std.450"],
                instruction=cls,
                operands=(operand1, operand2, operand3),
            )
        )


@dataclass
class UClamp(
    BinaryArithmeticOperator[OpTypeInt, None, Unsigned, None],
    GLSLExtensionOperator,
):
    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        operand1 = context.get_random_operand(
            Or(And(IsVectorType, IsOfUnsignedIntegerBaseType), IsScalarSignedInteger)
        )
        operand2 = context.get_random_operand(HasType(operand1.type))
        operand3 = context.get_random_operand(HasType(operand1.type))
        return FuzzResult(
            OpExtInst(
                type=operand1.type,
                extension_set=context.extension_sets["GLSL.std.450"],
                instruction=cls,
                operands=(operand1, operand2, operand3),
            )
        )


@dataclass
class SClamp(
    BinaryArithmeticOperator[OpTypeInt, None, Signed, None],
    GLSLExtensionOperator,
):
    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        operand1 = context.get_random_operand(
            Or(And(IsVectorType, IsOfSignedIntegerBaseType), IsScalarSignedInteger)
        )
        operand2 = context.get_random_operand(HasType(operand1.type))
        operand3 = context.get_random_operand(HasType(operand1.type))
        return FuzzResult(
            OpExtInst(
                type=operand1.type,
                extension_set=context.extension_sets["GLSL.std.450"],
                instruction=cls,
                operands=(operand1, operand2, operand3),
            )
        )


@dataclass
class FMix(
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        operand1 = context.get_random_operand(
            Or(And(IsVectorType, IsOfFloatBaseType), IsScalarFloat)
        )
        operand2 = context.get_random_operand(HasType(operand1.type))
        operand3 = context.get_random_operand(HasType(operand1.type))
        return FuzzResult(
            OpExtInst(
                type=operand1.type,
                extension_set=context.extension_sets["GLSL.std.450"],
                instruction=cls,
                operands=(operand1, operand2, operand3),
            )
        )


@dataclass
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
#         operand2 = context.get_random_operand(HasType(operand1.type))
#         operand3 = context.get_random_operand(HasType(operand1.type))
#         return [
#             OpExtInst(
#                 type=operand1.type,
#                 extension_set=context.extension_sets["GLSL.std.450"],
#                 instruction=self.__class__,
#                 operands=(operand1, operand2, operand3),
#             )
#         ]


# @dataclass
# class Fma(
#     BinaryArithmeticOperator[OpTypeFloat, None, None, None],
#     GLSLExtensionOperator,
# ):
#     @classmethod
#     def fuzz(cls, context: "Context") -> FuzzResult[Self]:
#         operand1 = context.get_random_operand(
#             Or(And(IsVectorType, IsOfFloatBaseType), IsScalarFloat)
#         )
#         operand2 = context.get_random_operand(HasType(operand1.type))
#         operand3 = context.get_random_operand(HasType(operand1.type))
#         ext_inst = OpExtInst(
#             type=operand1.type,
#             extension_set=context.extension_sets["GLSL.std.450"],
#             instruction=cls,
#             operands=(operand1, operand2, operand3),
#         )
#         # Required for determinism
#         context.add_annotation(
#             OpDecorate(target=ext_inst, decoration=Decoration.NoContraction)
#         )
#         return FuzzResult(ext_inst)


@dataclass
class FrexpStruct(
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        operand = context.get_random_operand(
            Or(And(IsVectorType, IsOfFloatBaseType), IsScalarFloat)
        )
        inner_type1 = operand.type
        if IsVectorType(operand):
            inner_type2 = OpTypeVector(OpTypeInt(32, 1), len(inner_type1))
        else:
            inner_type2 = OpTypeInt(32, 1)
        struct_type = OpTypeStruct((inner_type1, inner_type2))
        context.add_to_tvc(inner_type2)
        context.add_to_tvc(struct_type)
        return FuzzResult(
            OpExtInst(
                type=struct_type,
                extension_set=context.extension_sets["GLSL.std.450"],
                instruction=cls,
                operands=(operand,),
            ),
            [struct_type],
        )


# # # # # # # # # # # # # # # #
# TODO: packing and unpacking #
# # # # # # # # # # # # # # # #


# # # # # # # # # # # # # # # #


@dataclass
class Length(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        operand = context.get_random_operand(And(IsVectorType, IsOfFloatBaseType))
        result_type = OpTypeFloat(32)
        return FuzzResult(
            OpExtInst(
                type=result_type,
                extension_set=context.extension_sets["GLSL.std.450"],
                instruction=cls,
                operands=(operand,),
            ),
            [result_type],
        )


@dataclass
class Distance(
    BinaryOperatorFuzzMixin,
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        operand1 = context.get_random_operand(And(IsVectorType, IsOfFloatBaseType))
        operand2 = context.get_random_operand(HasType(operand1.type))
        result_type = OpTypeFloat(32)
        return FuzzResult(
            OpExtInst(
                type=result_type,
                extension_set=context.extension_sets["GLSL.std.450"],
                instruction=cls,
                operands=(
                    operand1,
                    operand2,
                ),
            ),
            [result_type],
        )


@dataclass
class Cross(
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        operand1 = context.get_random_operand(
            And(IsVectorType, IsOfFloatBaseType, HasLength(3))
        )
        operand2 = context.get_random_operand(HasType(operand1.type))
        return FuzzResult(
            OpExtInst(
                type=operand1.type,
                extension_set=context.extension_sets["GLSL.std.450"],
                instruction=cls,
                operands=(operand1, operand2),
            )
        )


@dataclass
class Normalize(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class FaceForward(
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        operand1 = context.get_random_operand(
            Or(And(IsVectorType, IsOfFloatBaseType), IsScalarFloat)
        )
        operand2 = context.get_random_operand(HasType(operand1.type))
        operand3 = context.get_random_operand(HasType(operand1.type))
        return FuzzResult(
            OpExtInst(
                type=operand1.type,
                extension_set=context.extension_sets["GLSL.std.450"],
                instruction=cls,
                operands=(operand1, operand2, operand3),
            )
        )


@dataclass
class Reflect(
    BinaryOperatorFuzzMixin,
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


# # TODO
# class Refract:
#     ...


@dataclass
class FindILsb(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeInt, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class FindSMsb(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeInt, None, Signed, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
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


@dataclass
class NMin(
    BinaryOperatorFuzzMixin,
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class NMax(
    BinaryOperatorFuzzMixin,
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


@dataclass
class NClamp(
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        operand1 = context.get_random_operand(
            Or(And(IsVectorType, IsOfFloatBaseType), IsScalarFloat)
        )
        operand2 = context.get_random_operand(HasType(operand1.type))
        operand3 = context.get_random_operand(HasType(operand1.type))
        return FuzzResult(
            OpExtInst(
                type=operand1.type,
                extension_set=context.extension_sets["GLSL.std.450"],
                instruction=cls,
                operands=(operand1, operand2, operand3),
            )
        )
