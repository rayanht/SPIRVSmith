import copy
from typing import TYPE_CHECKING

from src import OpCode
from src import Signed
from src import Type
from src import Unsigned
from src.annotations import OpDecorate
from src.enums import Decoration
from src.operators import BinaryOperatorFuzzMixin
from src.operators import Operand
from src.operators import UnaryOperatorFuzzMixin
from src.operators.arithmetic import BinaryArithmeticOperator
from src.operators.arithmetic import UnaryArithmeticOperator
from src.predicates import And
from src.predicates import HasFloatBaseType
from src.predicates import HasLength
from src.predicates import HasSignedIntegerBaseType
from src.predicates import HasType
from src.predicates import HasUnsignedIntegerBaseType
from src.predicates import IsMatrixType
from src.predicates import IsScalarFloat
from src.predicates import IsScalarSignedInteger
from src.predicates import IsVectorType
from src.predicates import Or
from src.types.concrete_types import OpTypeFloat
from src.types.concrete_types import OpTypeInt
from src.types.concrete_types import OpTypeStruct

if TYPE_CHECKING:
    from src.context import Context


class GLSLExtensionOperator:
    ...


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


class Inversesqrt(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class Determinant(
    UnaryArithmeticOperator[None, None, None, None], GLSLExtensionOperator
):
    type: Type = None
    operand: Operand = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        operand = context.get_random_operand(
            lambda x: IsMatrixType(x) and len(x.type) == len(x.type.type)
        )
        self.type = operand.get_base_type()
        self.operand1 = operand
        return [self]


# TODO: investigate how to recondition this, there is undefined behaviour if the matrix is singular or nearly singular, disabled for now
# class MatrixInverse(
#     UnaryArithmeticOperator[None, None, None, None], GLSLExtensionOperator
# ):
#     type: Type = None
#     operand: Operand = None

#     def fuzz(self, context: "Context") -> list[OpCode]:
#         operand = context.get_random_operand(lambda x: IsMatrixType(x) and len(x.type) == len(x.type.type))
#         self.type = operand1.get_base_type()
#         self.operand = operand
#         return [self]


class ModfStruct(
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    type: Type = None
    operand: Operand = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        operand = context.get_random_operand(
            Or(And(IsVectorType, HasFloatBaseType), IsScalarFloat)
        )
        self.type = OpTypeStruct()
        self.type.types = (operand.get_base_type(), operand.get_base_type())
        context.add_to_tvc(self.type)
        return [self]


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
    type: Type = None
    operand1: Operand = None
    operand2: Operand = None
    operand3: Operand = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        operand1 = context.get_random_operand(
            Or(And(IsVectorType, HasFloatBaseType), IsScalarFloat)
        )
        operand2 = context.get_random_operand(HasType(operand1.type))
        operand3 = context.get_random_operand(HasType(operand1.type))
        self.type = operand1.type
        self.operand1 = operand1
        self.operand2 = operand2
        self.operand3 = operand3
        return [self]


class UClamp(
    BinaryArithmeticOperator[OpTypeInt, None, Unsigned, None],
    GLSLExtensionOperator,
):
    type: Type = None
    operand1: Operand = None
    operand2: Operand = None
    operand3: Operand = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        operand1 = context.get_random_operand(
            Or(And(IsVectorType, HasUnsignedIntegerBaseType), IsScalarSignedInteger)
        )
        operand2 = context.get_random_operand(HasType(operand1.type))
        operand3 = context.get_random_operand(HasType(operand1.type))
        self.type = operand1.type
        self.operand1 = operand1
        self.operand2 = operand2
        self.operand3 = operand3
        return [self]


class SClamp(
    BinaryArithmeticOperator[OpTypeInt, None, Signed, None],
    GLSLExtensionOperator,
):
    type: Type = None
    operand1: Operand = None
    operand2: Operand = None
    operand3: Operand = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        operand1 = context.get_random_operand(
            Or(And(IsVectorType, HasSignedIntegerBaseType), IsScalarSignedInteger)
        )
        operand2 = context.get_random_operand(HasType(operand1.type))
        operand3 = context.get_random_operand(HasType(operand1.type))
        self.type = operand1.type
        self.operand1 = operand1
        self.operand2 = operand2
        self.operand3 = operand3
        return [self]


class FMix(
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    type: Type = None
    operand1: Operand = None
    operand2: Operand = None
    operand3: Operand = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        operand1 = context.get_random_operand(
            Or(And(IsVectorType, HasFloatBaseType), IsScalarFloat)
        )
        operand2 = context.get_random_operand(HasType(operand1.type))
        operand3 = context.get_random_operand(HasType(operand1.type))
        self.type = operand1.type
        self.operand1 = operand1
        self.operand2 = operand2
        self.operand3 = operand3
        return [self]


class Step(
    BinaryOperatorFuzzMixin,
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    ...


class SmoothStep(
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    type: Type = None
    operand1: Operand = None
    operand2: Operand = None
    operand3: Operand = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        operand1 = context.get_random_operand(
            Or(And(IsVectorType, HasFloatBaseType), IsScalarFloat)
        )
        operand2 = context.get_random_operand(HasType(operand1.type))
        operand3 = context.get_random_operand(HasType(operand1.type))
        self.type = operand1.type
        self.operand1 = operand1
        self.operand2 = operand2
        self.operand3 = operand3
        return [self]


class Fma(
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    type: Type = None
    operand1: Operand = None
    operand2: Operand = None
    operand3: Operand = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        operand1 = context.get_random_operand(
            Or(And(IsVectorType, HasFloatBaseType), IsScalarFloat)
        )
        operand2 = context.get_random_operand(HasType(operand1.type))
        operand3 = context.get_random_operand(HasType(operand1.type))
        self.type = operand1.type
        self.operand1 = operand1
        self.operand2 = operand2
        self.operand3 = operand3
        # Required for determinism
        context.add_annotation(OpDecorate(self, decoration=Decoration.NoContraction))
        return [self]


class FrexpStruct(
    UnaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    type: Type = None
    operand: Operand = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        operand = context.get_random_operand(
            Or(And(IsVectorType, HasFloatBaseType), IsScalarFloat)
        )
        self.type = OpTypeStruct()
        inner_type1 = operand.type
        inner_type2 = copy.deepcopy(inner_type1)
        inner_type2.type = OpTypeInt()
        inner_type2.type.width = 32
        inner_type2.type.signed = 1
        context.add_to_tvc(inner_type2)
        self.type.types = (inner_type1, inner_type2)
        context.add_to_tvc(self.type)
        return [self]


# # # # # # # # # # # # # # # #
# TODO: packing and unpacking #
# # # # # # # # # # # # # # # #


# # # # # # # # # # # # # # # #


class Length(
    UnaryOperatorFuzzMixin,
    UnaryArithmeticOperator[OpTypeFloat, OpTypeFloat, None, None],
    GLSLExtensionOperator,
):
    ...


class Distance(
    BinaryOperatorFuzzMixin,
    BinaryArithmeticOperator[OpTypeFloat, OpTypeFloat, None, None],
    GLSLExtensionOperator,
):
    ...


class Cross(
    BinaryArithmeticOperator[OpTypeFloat, None, None, None],
    GLSLExtensionOperator,
):
    type: Type = None
    operand1: Operand = None
    operand2: Operand = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        operand1 = context.get_random_operand(
            And(IsVectorType, HasFloatBaseType, HasLength(3))
        )
        operand2 = context.get_random_operand(HasType(operand1.type))
        self.type = operand1.type
        self.operand1 = operand1
        self.operand2 = operand2
        return [self]


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
    type: Type = None
    operand1: Operand = None
    operand2: Operand = None
    operand3: Operand = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        operand1 = context.get_random_operand(
            Or(And(IsVectorType, HasFloatBaseType), IsScalarFloat)
        )
        operand2 = context.get_random_operand(HasType(operand1.type))
        operand3 = context.get_random_operand(HasType(operand1.type))
        self.type = operand1.type
        self.operand1 = operand1
        self.operand2 = operand2
        self.operand3 = operand3
        return [self]


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
    type: Type = None
    operand1: Operand = None
    operand2: Operand = None
    operand3: Operand = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        operand1 = context.get_random_operand(
            Or(And(IsVectorType, HasFloatBaseType), IsScalarFloat)
        )
        operand2 = context.get_random_operand(HasType(operand1.type))
        operand3 = context.get_random_operand(HasType(operand1.type))
        self.type = operand1.type
        self.operand1 = operand1
        self.operand2 = operand2
        self.operand3 = operand3
        return [self]
