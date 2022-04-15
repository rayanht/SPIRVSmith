from typing import (
    Callable,
    Generic,
    Optional,
    TypeVar,
)
from src import Signed, Statement, Unsigned

from src.constants import Constant
from src.operators import BinaryOperatorFuzzMixin, UnaryOperatorFuzzMixin
from src.predicates import (
    HasValidBaseTypeAndSign,
    IsValidArithmeticOperand,
)

from src.types.concrete_types import (
    OpTypeFloat,
    OpTypeInt,
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


# class OpVectorTimesScalar(BinaryOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeVector, None, None, None]):
#     ...
