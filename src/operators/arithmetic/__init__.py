from typing import Callable
from typing import ClassVar
from typing import Generic
from typing import Optional
from typing import TypeVar

from src import Statement
from src.operators import Operand
from src.patched_dataclass import dataclass
from src.predicates import HasValidBaseTypeAndSign
from src.predicates import IsArithmeticType


S = TypeVar("S")
D = TypeVar("D")
SC = TypeVar("SC")
DC = TypeVar("DC")


@dataclass
class ArithmeticOperator(Statement, Generic[S, D, SC, DC]):
    OPERAND_SELECTION_PREDICATE: ClassVar[
        Callable[[Operand], bool]
    ] = lambda target_type, signed: lambda op: IsArithmeticType(
        op
    ) and HasValidBaseTypeAndSign(
        op, target_type, signed
    )


@dataclass
class UnaryArithmeticOperator(
    ArithmeticOperator[S, Optional[D], Optional[SC], Optional[DC]]
):
    operand1: Operand


@dataclass
class BinaryArithmeticOperator(
    ArithmeticOperator[S, Optional[D], Optional[SC], Optional[DC]]
):
    operand1: Operand
    operand2: Operand
