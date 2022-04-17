from typing import (
    Callable,
    Generic,
    Optional,
    TypeVar,
)
from src import Signed, Statement, Unsigned

from src.constants import Constant
from src.operators import UnaryOperatorFuzzMixin
from src.predicates import HasValidBaseTypeAndSign, IsConversionOperand


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
