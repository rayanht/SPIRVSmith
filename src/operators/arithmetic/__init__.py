from typing import Callable
from typing import Generic
from typing import Optional
from typing import TypeVar

from src import Statement
from src import Type
from src.operators import Operand
from src.predicates import HasValidBaseTypeAndSign
from src.predicates import IsOfType
from src.types.abstract_types import ArithmeticType


S = TypeVar("S")
D = TypeVar("D")
SC = TypeVar("SC")
DC = TypeVar("DC")


class ArithmeticOperator(Statement, Generic[S, D, SC, DC]):
    OPERAND_SELECTION_PREDICATE: Callable[
        [Operand], bool
    ] = lambda _, target_type, signed: lambda op: IsOfType(ArithmeticType)(
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
