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

from src.constants import Constant
from src.operators import BinaryOperatorFuzzMixin, UnaryOperatorFuzzMixin
from src.predicates import (
    HasValidBaseType,
    HasValidBaseTypeAndSign,
    IsValidBitwiseOperand,
)

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

    def to_spasm(self, context: "Context") -> str:
        return f"%{self.id} = {self.__class__.__name__} %{context.tvc[self.type]} %{self.operand.id}"


class BinaryBitwiseOperator(
    BitwiseOperator[S, Optional[D], Optional[SC], Optional[DC]]
):
    type: Type = None
    operand1: Operand = None
    operand2: Operand = None

    def to_spasm(self, context: "Context") -> str:
        return f"%{self.id} = {self.__class__.__name__} %{context.tvc[self.type]} %{self.operand1.id} %{self.operand2.id}"


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
