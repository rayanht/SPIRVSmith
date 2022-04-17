from typing import Callable
from typing import Generic
from typing import Optional
from typing import TypeVar

from src import Statement
from src.constants import Constant
from src.operators import BinaryOperatorFuzzMixin
from src.operators import UnaryOperatorFuzzMixin
from src.predicates import HasValidBaseTypeAndSign
from src.predicates import IsValidBitwiseOperand
from src.types.concrete_types import OpTypeInt
from src.types.concrete_types import Type

Operand = Statement | Constant

S = TypeVar("S")
D = TypeVar("D")
SC = TypeVar("SC")
DC = TypeVar("DC")


class BitwiseOperator(Statement, Generic[S, D, SC, DC]):
    OPERAND_SELECTION_PREDICATE: Callable[
        [Operand], bool
    ] = lambda _, target_type, signed: lambda op: IsValidBitwiseOperand(
        op
    ) and HasValidBaseTypeAndSign(
        op, target_type, signed
    )


class UnaryBitwiseOperator(BitwiseOperator[S, Optional[D], Optional[SC], Optional[DC]]):
    type: Type = None
    operand: Operand = None


class BinaryBitwiseOperator(
    BitwiseOperator[S, Optional[D], Optional[SC], Optional[DC]]
):
    type: Type = None
    operand1: Operand = None
    operand2: Operand = None


class OpShiftRightLogical(
    BinaryOperatorFuzzMixin, BinaryBitwiseOperator[OpTypeInt, None, None, None]
):
    ...


class OpShiftRightArithmetic(
    BinaryOperatorFuzzMixin, BinaryBitwiseOperator[OpTypeInt, None, None, None]
):
    ...


class OpShiftLeftLogical(
    BinaryOperatorFuzzMixin, BinaryBitwiseOperator[OpTypeInt, None, None, None]
):
    ...


class OpBitwiseOr(
    BinaryOperatorFuzzMixin, BinaryBitwiseOperator[OpTypeInt, None, None, None]
):
    ...


class OpBitwiseXor(
    BinaryOperatorFuzzMixin, BinaryBitwiseOperator[OpTypeInt, None, None, None]
):
    ...


class OpBitwiseAnd(
    BinaryOperatorFuzzMixin, BinaryBitwiseOperator[OpTypeInt, None, None, None]
):
    ...


class OpNot(UnaryOperatorFuzzMixin, UnaryBitwiseOperator[OpTypeInt, None, None, None]):
    ...


class OpBitCount(
    UnaryOperatorFuzzMixin, UnaryBitwiseOperator[OpTypeInt, None, None, None]
):
    ...
