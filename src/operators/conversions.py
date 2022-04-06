import random
from types import NoneType

from typing import (
    TYPE_CHECKING,
    Callable,
    Generic,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
    get_args,
)
from src import OpCode, Signed, Statement, Unsigned

from src.constants import Constant, OpConstantComposite
from src.operators import UnaryOperatorFuzzMixin
from src.predicates import HasValidBaseTypeAndSign, IsConversionOperand

if TYPE_CHECKING:
    from src.context import Context
from src.types.abstract_types import (
    NumericalType,
)
from src.types.concrete_types import (
    OpTypeBool,
    OpTypeFloat,
    OpTypeInt,
    OpTypeVector,
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

    def to_spasm(self, context: "Context") -> str:
        return f"%{self.id} = {self.__class__.__name__} %{context.tvc[self.type]} %{self.operand.id}"


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
