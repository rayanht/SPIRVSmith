from typing import Callable
from typing import ClassVar
from typing import Generic
from typing import Optional
from typing import TypeVar

from src import Signed
from src import Statement
from src import Unsigned
from src.operators import Operand
from src.operators import UnaryOperatorFuzzMixin
from src.patched_dataclass import dataclass
from src.predicates import HasValidBaseTypeAndSign
from src.predicates import IsArithmeticType
from src.types.concrete_types import OpTypeFloat
from src.types.concrete_types import OpTypeInt

S = TypeVar("S")
D = TypeVar("D")
SC = TypeVar("SC")
DC = TypeVar("DC")


@dataclass
class ConversionOperator(Statement, Generic[S, D, SC, DC]):
    OPERAND_SELECTION_PREDICATE: ClassVar[
        Callable[[Operand], bool]
    ] = lambda target_type, signed: lambda op: IsArithmeticType(
        op
    ) and HasValidBaseTypeAndSign(
        op, target_type, signed
    )


@dataclass
class UnaryConversionOperator(ConversionOperator[S, D, Optional[SC], Optional[DC]]):
    operand1: Operand


@dataclass
class OpConvertFToU(
    UnaryOperatorFuzzMixin,
    UnaryConversionOperator[OpTypeFloat, OpTypeInt, None, Unsigned],
):
    ...


@dataclass
class OpConvertFToS(
    UnaryOperatorFuzzMixin,
    UnaryConversionOperator[OpTypeFloat, OpTypeInt, None, Signed],
):
    ...


@dataclass
class OpConvertSToF(
    UnaryOperatorFuzzMixin,
    UnaryConversionOperator[OpTypeInt, OpTypeFloat, Signed, None],
):
    ...


@dataclass
class OpConvertUToF(
    UnaryOperatorFuzzMixin,
    UnaryConversionOperator[OpTypeInt, OpTypeFloat, Unsigned, None],
):
    ...
