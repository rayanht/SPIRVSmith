from typing import Callable
from typing import ClassVar
from typing import Generic
from typing import Optional
from typing import TYPE_CHECKING
from typing import TypeVar

from typing_extensions import Self

from src import FuzzResult
from src import Signed
from src import Statement
from src import Unsigned
from src.operators import BinaryOperatorFuzzMixin
from src.operators import Operand
from src.operators import UnaryOperatorFuzzMixin
from src.patched_dataclass import dataclass
from src.predicates import And
from src.predicates import HasBaseType
from src.predicates import HasValidBaseTypeAndSign
from src.predicates import IsArithmeticType
from src.predicates import IsOfType
from src.predicates import IsVectorType
from src.predicates import Or
from src.types.concrete_types import OpTypeBool
from src.types.concrete_types import OpTypeFloat
from src.types.concrete_types import OpTypeInt

if TYPE_CHECKING:
    from src.context import Context
S = TypeVar("S")
D = TypeVar("D")
SC = TypeVar("SC")
DC = TypeVar("DC")


@dataclass
class LogicalOperator(Statement, Generic[S, D, SC, DC]):
    OPERAND_SELECTION_PREDICATE: ClassVar[
        Callable[[Operand], bool]
    ] = lambda target_type, signed: lambda op: Or(
        IsArithmeticType, IsOfType(OpTypeBool)
    )(
        op
    ) and HasValidBaseTypeAndSign(
        op, target_type, signed
    )


@dataclass
class UnaryLogicalOperator(LogicalOperator[S, Optional[D], Optional[SC], Optional[DC]]):
    operand1: Operand


@dataclass
class BinaryLogicalOperator(
    LogicalOperator[S, Optional[D], Optional[SC], Optional[DC]]
):
    operand1: Operand
    operand2: Operand


class OpAny(UnaryLogicalOperator[OpTypeBool, None, None, None]):
    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        operand1: Operand = context.get_random_operand(
            And(IsVectorType, HasBaseType(OpTypeBool()))
        )
        result_type: OpTypeBool = OpTypeBool()
        return FuzzResult(cls(result_type, operand1), [result_type])


class OpAll(UnaryLogicalOperator[OpTypeBool, None, None, None]):
    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        operand1: Operand = context.get_random_operand(
            And(IsVectorType, HasBaseType(OpTypeBool()))
        )
        result_type: OpTypeBool = OpTypeBool()
        return FuzzResult(cls(result_type, operand1), [result_type])


@dataclass
class OpIsNan(
    UnaryOperatorFuzzMixin, UnaryLogicalOperator[OpTypeFloat, OpTypeBool, None, None]
):
    ...


@dataclass
class OpIsInf(
    UnaryOperatorFuzzMixin, UnaryLogicalOperator[OpTypeFloat, OpTypeBool, None, None]
):
    ...


@dataclass
class OpLogicalEqual(
    BinaryOperatorFuzzMixin, BinaryLogicalOperator[OpTypeBool, OpTypeBool, None, None]
):
    ...


@dataclass
class OpLogicalNotEqual(
    BinaryOperatorFuzzMixin, BinaryLogicalOperator[OpTypeBool, OpTypeBool, None, None]
):
    ...


@dataclass
class OpLogicalOr(
    BinaryOperatorFuzzMixin, BinaryLogicalOperator[OpTypeBool, OpTypeBool, None, None]
):
    ...


@dataclass
class OpLogicalAnd(
    BinaryOperatorFuzzMixin, BinaryLogicalOperator[OpTypeBool, OpTypeBool, None, None]
):
    ...


@dataclass
class OpLogicalNot(
    UnaryOperatorFuzzMixin, UnaryLogicalOperator[OpTypeBool, OpTypeBool, None, None]
):
    ...


@dataclass
class OpIEqual(
    BinaryOperatorFuzzMixin, BinaryLogicalOperator[OpTypeInt, OpTypeBool, None, None]
):
    ...


@dataclass
class OpINotEqual(
    BinaryOperatorFuzzMixin, BinaryLogicalOperator[OpTypeInt, OpTypeBool, None, None]
):
    ...


class OpUGreaterThan(
    BinaryOperatorFuzzMixin,
    BinaryLogicalOperator[OpTypeInt, OpTypeBool, Unsigned, None],
):
    ...


@dataclass
class OpSGreaterThan(
    BinaryOperatorFuzzMixin, BinaryLogicalOperator[OpTypeInt, OpTypeBool, Signed, None]
):
    ...


@dataclass
class OpUGreaterThanEqual(
    BinaryOperatorFuzzMixin,
    BinaryLogicalOperator[OpTypeInt, OpTypeBool, Unsigned, None],
):
    ...


@dataclass
class OpSGreaterThanEqual(
    BinaryOperatorFuzzMixin, BinaryLogicalOperator[OpTypeInt, OpTypeBool, Signed, None]
):
    ...


@dataclass
class OpULessThan(
    BinaryOperatorFuzzMixin,
    BinaryLogicalOperator[OpTypeInt, OpTypeBool, Unsigned, None],
):
    ...


@dataclass
class OpSLessThan(
    BinaryOperatorFuzzMixin, BinaryLogicalOperator[OpTypeInt, OpTypeBool, Signed, None]
):
    ...


@dataclass
class OpULessThanEqual(
    BinaryOperatorFuzzMixin,
    BinaryLogicalOperator[OpTypeInt, OpTypeBool, Unsigned, None],
):
    ...


@dataclass
class OpSLessThanEqual(
    BinaryOperatorFuzzMixin, BinaryLogicalOperator[OpTypeInt, OpTypeBool, Signed, None]
):
    ...


@dataclass
class OpFOrdEqual(
    BinaryOperatorFuzzMixin, BinaryLogicalOperator[OpTypeFloat, OpTypeBool, None, None]
):
    ...


@dataclass
class OpFUnordEqual(
    BinaryOperatorFuzzMixin, BinaryLogicalOperator[OpTypeFloat, OpTypeBool, None, None]
):
    ...


@dataclass
class OpFOrdNotEqual(
    BinaryOperatorFuzzMixin, BinaryLogicalOperator[OpTypeFloat, OpTypeBool, None, None]
):
    ...


@dataclass
class OpFUnordNotEqual(
    BinaryOperatorFuzzMixin, BinaryLogicalOperator[OpTypeFloat, OpTypeBool, None, None]
):
    ...


@dataclass
class OpFOrdLessThan(
    BinaryOperatorFuzzMixin, BinaryLogicalOperator[OpTypeFloat, OpTypeBool, None, None]
):
    ...


@dataclass
class OpFUnordLessThan(
    BinaryOperatorFuzzMixin, BinaryLogicalOperator[OpTypeFloat, OpTypeBool, None, None]
):
    ...


@dataclass
class OpFOrdGreaterThan(
    BinaryOperatorFuzzMixin, BinaryLogicalOperator[OpTypeFloat, OpTypeBool, None, None]
):
    ...


@dataclass
class OpFUnordGreaterThan(
    BinaryOperatorFuzzMixin, BinaryLogicalOperator[OpTypeFloat, OpTypeBool, None, None]
):
    ...


@dataclass
class OpFOrdLessThanEqual(
    BinaryOperatorFuzzMixin, BinaryLogicalOperator[OpTypeFloat, OpTypeBool, None, None]
):
    ...


@dataclass
class OpFUnordLessThanEqual(
    BinaryOperatorFuzzMixin, BinaryLogicalOperator[OpTypeFloat, OpTypeBool, None, None]
):
    ...


@dataclass
class OpFOrdGreaterThanEqual(
    BinaryOperatorFuzzMixin, BinaryLogicalOperator[OpTypeFloat, OpTypeBool, None, None]
):
    ...


@dataclass
class OpFUnordGreaterThanEqual(
    BinaryOperatorFuzzMixin, BinaryLogicalOperator[OpTypeFloat, OpTypeBool, None, None]
):
    ...
