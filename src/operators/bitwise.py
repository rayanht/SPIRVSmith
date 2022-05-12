from typing import Callable
from typing import ClassVar
from typing import Generic
from typing import Optional
from typing import TypeVar

from src import Statement
from src.operators import BinaryOperatorFuzzMixin
from src.operators import Operand
from src.operators import UnaryOperatorFuzzMixin
from src.patched_dataclass import dataclass
from src.predicates import HasValidBaseTypeAndSign
from src.predicates import IsArithmeticType
from src.types.concrete_types import OpTypeInt

S = TypeVar("S")
D = TypeVar("D")
SC = TypeVar("SC")
DC = TypeVar("DC")


@dataclass
class BitwiseOperator(Statement, Generic[S, D, SC, DC]):
    OPERAND_SELECTION_PREDICATE: ClassVar[
        Callable[[Operand], bool]
    ] = lambda target_type, signed: lambda op: IsArithmeticType(
        op
    ) and HasValidBaseTypeAndSign(
        op, target_type, signed
    )


@dataclass
class UnaryBitwiseOperator(BitwiseOperator[S, Optional[D], Optional[SC], Optional[DC]]):
    operand1: Operand


@dataclass
class BinaryBitwiseOperator(
    BitwiseOperator[S, Optional[D], Optional[SC], Optional[DC]]
):
    operand1: Operand
    operand2: Operand


@dataclass
class OpShiftRightLogical(
    BinaryOperatorFuzzMixin, BinaryBitwiseOperator[OpTypeInt, None, None, None]
):
    ...


@dataclass
class OpShiftRightArithmetic(
    BinaryOperatorFuzzMixin, BinaryBitwiseOperator[OpTypeInt, None, None, None]
):
    ...


@dataclass
class OpShiftLeftLogical(
    BinaryOperatorFuzzMixin, BinaryBitwiseOperator[OpTypeInt, None, None, None]
):
    ...


@dataclass
class OpBitwiseOr(
    BinaryOperatorFuzzMixin, BinaryBitwiseOperator[OpTypeInt, None, None, None]
):
    ...


@dataclass
class OpBitwiseXor(
    BinaryOperatorFuzzMixin, BinaryBitwiseOperator[OpTypeInt, None, None, None]
):
    ...


@dataclass
class OpBitwiseAnd(
    BinaryOperatorFuzzMixin, BinaryBitwiseOperator[OpTypeInt, None, None, None]
):
    ...


@dataclass
class OpNot(UnaryOperatorFuzzMixin, UnaryBitwiseOperator[OpTypeInt, None, None, None]):
    ...


@dataclass
class OpBitCount(
    UnaryOperatorFuzzMixin, UnaryBitwiseOperator[OpTypeInt, None, None, None]
):
    ...
