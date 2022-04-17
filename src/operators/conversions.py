from typing import Callable
from typing import Generic
from typing import Optional
from typing import TypeVar

from src import Signed
from src import Statement
from src import Unsigned
from src.constants import Constant
from src.operators import UnaryOperatorFuzzMixin
from src.predicates import HasValidBaseTypeAndSign
from src.predicates import IsConversionOperand
from src.types.concrete_types import OpTypeFloat
from src.types.concrete_types import OpTypeInt
from src.types.concrete_types import Type

Operand = Statement | Constant

S = TypeVar("S")
D = TypeVar("D")
SC = TypeVar("SC")
DC = TypeVar("DC")


class ConversionOperator(Statement, Generic[S, D, SC, DC]):
    OPERAND_SELECTION_PREDICATE: Callable[
        [Statement], bool
    ] = lambda _, target_type, signed: lambda op: IsConversionOperand(
        op
    ) and HasValidBaseTypeAndSign(
        op, target_type, signed
    )


class UnaryConversionOperator(ConversionOperator[S, D, Optional[SC], Optional[DC]]):
    type: Type = None
    operand: Operand = None


class OpConvertFToU(
    UnaryOperatorFuzzMixin,
    UnaryConversionOperator[OpTypeFloat, OpTypeInt, None, Unsigned],
):
    ...


class OpConvertFToS(
    UnaryOperatorFuzzMixin,
    UnaryConversionOperator[OpTypeFloat, OpTypeInt, None, Signed],
):
    ...


class OpConvertSToF(
    UnaryOperatorFuzzMixin,
    UnaryConversionOperator[OpTypeInt, OpTypeFloat, Signed, None],
):
    ...


class OpConvertUToF(
    UnaryOperatorFuzzMixin,
    UnaryConversionOperator[OpTypeInt, OpTypeFloat, Unsigned, None],
):
    ...


# class OpUConvert(UnaryConversionOperator[OpTypeInt, Unsigned]):
#     ...
