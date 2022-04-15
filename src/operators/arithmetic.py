from typing import (
    TYPE_CHECKING,
    Callable,
    Generic,
    Optional,
    TypeVar,
)
from src import OpCode, Signed, Statement, Unsigned

from src.constants import Constant

if TYPE_CHECKING:
    from src.context import Context
from src.operators import BinaryOperatorFuzzMixin, UnaryOperatorFuzzMixin
from src.predicates import (
    HasValidBaseType,
    HasValidBaseTypeAndSign,
    HasValidType,
    HaveSameTypeLength,
    IsMatrixType,
    IsScalarFloat,
    IsValidArithmeticOperand,
    IsVectorType,
)

from src.types.concrete_types import (
    OpTypeFloat,
    OpTypeInt,
    OpTypeMatrix,
    OpTypeVector,
    Type,
)

Operand = Statement | Constant

S = TypeVar("S")
D = TypeVar("D")
SC = TypeVar("SC")
DC = TypeVar("DC")


class ArithmeticOperator(Statement, Generic[S, D, SC, DC]):
    OPERAND_SELECTION_PREDICATE: Callable[
        [Operand], bool
    ] = lambda _, target_type, signed: lambda op: IsValidArithmeticOperand(
        op
    ) and HasValidBaseTypeAndSign(
        op, target_type, signed
    )


class UnaryArithmeticOperator(
    ArithmeticOperator[S, Optional[D], Optional[SC], Optional[DC]]
):
    type: Type = None
    operand: Operand = None


class BinaryArithmeticOperator(
    ArithmeticOperator[S, Optional[D], Optional[SC], Optional[DC]]
):
    type: Type = None
    operand1: Operand = None
    operand2: Operand = None


class OpSNegate(
    UnaryOperatorFuzzMixin, UnaryArithmeticOperator[OpTypeInt, None, Signed, None]
):
    ...


class OpFNegate(
    UnaryOperatorFuzzMixin, UnaryArithmeticOperator[OpTypeFloat, None, None, None]
):
    ...


class OpIAdd(
    BinaryOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeInt, None, None, None]
):
    ...


class OpFAdd(
    BinaryOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeFloat, None, None, None]
):
    ...


class OpISub(
    BinaryOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeInt, None, None, None]
):
    ...


class OpFSub(
    BinaryOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeFloat, None, None, None]
):
    ...


class OpIMul(
    BinaryOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeInt, None, None, None]
):
    ...


class OpFMul(
    BinaryOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeFloat, None, None, None]
):
    ...


class OpUDiv(
    BinaryOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeInt, None, Unsigned, None]
):
    ...


class OpSDiv(
    BinaryOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeInt, None, Signed, None]
):
    ...


class OpFDiv(
    BinaryOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeFloat, None, None, None]
):
    ...


class OpUMod(
    BinaryOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeInt, None, Unsigned, None]
):
    ...


class OpSRem(
    BinaryOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeInt, None, Signed, None]
):
    ...


class OpSMod(
    BinaryOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeInt, None, Signed, None]
):
    ...


class OpFRem(
    BinaryOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeFloat, None, None, None]
):
    ...


class OpFMod(
    BinaryOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeFloat, None, None, None]
):
    ...


# The following operators override the fuzzing logic rather than relying on the mixin
# This is because trying to encompass their logic in the mixin would be way too complex:

class OpVectorTimesScalar(BinaryArithmeticOperator[None, None, None, None]):
    type: OpTypeVector = None
    operand1: Operand = None
    operand2: Operand = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        operand1 = context.get_random_operand(
            lambda x: IsVectorType(x) and HasValidBaseType(x, OpTypeFloat)
        )
        if not operand1:
            return []
        operand2 = context.get_random_operand(IsScalarFloat)
        if not operand2:
            return []
        self.type = operand1.type
        self.operand1 = operand1
        self.operand2 = operand2
        return [self]

class OpMatrixTimesScalar(BinaryArithmeticOperator[None, None, None, None]):
    type: OpTypeMatrix = None
    operand1: Operand = None
    operand2: Operand = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        operand1 = context.get_random_operand(
            lambda x: IsMatrixType(x) and HasValidBaseType(x, OpTypeFloat)
        )
        if not operand1:
            return []
        operand2 = context.get_random_operand(IsScalarFloat)
        if not operand2:
            return []
        self.type = operand1.type
        self.operand1 = operand1
        self.operand2 = operand2
        return [self]
    
class OpVectorTimesMatrix(BinaryArithmeticOperator[None, None, None, None]):
    type: OpTypeVector = None
    operand1: Operand = None
    operand2: Operand = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        operand1 = context.get_random_operand(
            lambda x: IsVectorType(x) and HasValidBaseType(x, OpTypeFloat)
        )
        if not operand1:
            return []
        operand2 = context.get_random_operand(lambda x: IsMatrixType(x) and HasValidBaseType(x, OpTypeFloat) and HaveSameTypeLength(x, operand1))
        if not operand2:
            return []
        self.type = OpTypeVector()
        self.type.type = operand1.get_base_type()
        self.type.size = len(operand2.type.type)
        context.add_to_tvc(self.type)
        self.operand1 = operand1
        self.operand2 = operand2
        return [self]

class OpMatrixTimesVector(BinaryArithmeticOperator[None, None, None, None]):
    type: OpTypeVector = None
    operand1: Operand = None
    operand2: Operand = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        operand1 = context.get_random_operand(lambda x: IsMatrixType(x) and HasValidBaseType(x, OpTypeFloat))
        if not operand1:
            return []
        operand2 = context.get_random_operand(
            lambda x: IsVectorType(x) and HasValidBaseType(x, OpTypeFloat) and HaveSameTypeLength(x, operand1)
        )
        if not operand2:
            return []
        self.type = operand1.type.type
        self.operand1 = operand1
        self.operand2 = operand2
        return [self]
    
class OpMatrixTimesMatrix(BinaryArithmeticOperator[None, None, None, None]):
    type: OpTypeMatrix = None
    operand1: Operand = None
    operand2: Operand = None
    
    def fuzz(self, context: "Context") -> list[OpCode]:
        operand1 = context.get_random_operand(lambda x: IsMatrixType(x) and HasValidBaseType(x, OpTypeFloat))
        if not operand1:
            return []
        # Same number of columns that operand1 has rows
        operand2 = context.get_random_operand(lambda x: IsMatrixType(x) and HasValidBaseType(x, OpTypeFloat) and HaveSameTypeLength(x, operand1.type))
        if not operand2:
            return []
        self.type = OpTypeMatrix()
        self.type.type = operand1.type.type
        self.type.size = len(operand2.type)
        self.operand1 = operand1
        self.operand2 = operand2
        return [self]

class OpOuterProduct(BinaryArithmeticOperator[None, None, None, None]):
    type: OpTypeMatrix = None
    operand1: Operand = None
    operand2: Operand = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        predicate = lambda x: IsVectorType(x) and HasValidBaseType(x, OpTypeFloat)
        operand1 = context.get_random_operand(predicate)
        if not operand1:
            return []
        operand2 = context.get_random_operand(predicate)
        self.type = OpTypeMatrix()
        self.type.type = operand1.type
        self.type.size = len(operand2.type)
        context.add_to_tvc(self.type)
        self.operand1 = operand1
        self.operand2 = operand2
        return [self]

class OpDot(BinaryArithmeticOperator[None, None, None, None]):
    type: OpTypeFloat = None
    operand1: Operand = None
    operand2: Operand = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        predicate = lambda x: IsVectorType(x) and HasValidBaseType(x, OpTypeFloat)
        operand1 = context.get_random_operand(predicate)
        if not operand1:
            return []
        operand2 = context.get_random_operand(predicate, operand1)
        self.type = operand1.get_base_type()
        self.operand1 = operand1
        self.operand2 = operand2
        return [self]