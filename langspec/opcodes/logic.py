import random
from types import NoneType

from typing import (
    TYPE_CHECKING,
    Generic,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
    get_args,
)
from langspec.opcodes import OpCode, Signed, Statement, Unsigned

from langspec.opcodes.constants import Constant

if TYPE_CHECKING:
    from langspec.opcodes.context import Context
from langspec.opcodes.types.abstract_types import (
    NumericalType,
)
from langspec.opcodes.types.concrete_types import (
    OpTypeBool,
    OpTypeFloat,
    OpTypeInt,
    OpTypeVector,
    Type,
)


def find_logical_operands(
    context: "Context", target_type: Type, signed: bool | NoneType
) -> Tuple[Union[Statement, Constant], Union[Statement, Constant]]:
    operands: List[Statement] = context.get_typed_statements(
        lambda _: True
    ) + context.get_constants((OpTypeBool, OpTypeVector))
    eligible_operands: List[Union[Statement, Constant]] = []
    for operand in operands:
        if isinstance(operand.type, target_type) or (
            isinstance(operand.type, OpTypeVector)
            and isinstance(operand.type.type, target_type)
        ):
            if (
                isinstance(operand.type, NumericalType)
                or isinstance(operand.type, OpTypeVector)
                and isinstance(operand.type.type, NumericalType)
            ):
                if signed is not None and operand.type.signed != signed:
                    continue
            eligible_operands.append(operand)
    if len(eligible_operands) == 0:
        return None
    operand1 = random.choice(eligible_operands)
    if isinstance(operand1.type, OpTypeVector):
        operand2 = random.choice(
            list(
                filter(lambda op: isinstance(op.type, OpTypeVector), eligible_operands)
            )
        )
    elif isinstance(operand1.type, NumericalType):
        operand2 = random.choice(
            list(
                filter(lambda op: isinstance(op.type, NumericalType), eligible_operands)
            )
        )
    elif isinstance(operand1.type, OpTypeBool):
        operand2 = random.choice(
            list(filter(lambda op: isinstance(op.type, OpTypeBool), eligible_operands))
        )
    return operand1, operand2


T = TypeVar("T")
S = TypeVar("S")


class LogicalOperator(Statement, Generic[T, S]):
    pass


class UnaryLogicalOperatorFuzzMixin:
    def fuzz(self, context: "Context") -> List[OpCode]:
        target_type, constraint = get_args(self.__class__.__orig_bases__[1])
        signed = None
        if constraint != type(None):
            signed = constraint == type(Signed())
        operands = find_logical_operands(context, target_type, signed)
        if not operands:
            return []
        self.operand: Statement = operands[0]
        self.type = OpTypeBool()
        return [self]


class BinaryLogicalOperatorFuzzMixin:
    def fuzz(self, context: "Context") -> List[OpCode]:
        target_type, constraint = get_args(self.__class__.__orig_bases__[1])
        signed = None
        if constraint != type(None):
            signed = constraint == type(Signed())
        operands = find_logical_operands(context, target_type, signed)
        if not operands:
            return []
        self.operand1 = operands[0]
        self.operand2 = operands[1]
        self.type = OpTypeBool()
        return [self]


class UnaryLogicalOperator(LogicalOperator[T, Optional[S]]):
    type: Type = None
    operand: Union[Statement, Constant] = None

    def to_spasm(self, context: "Context") -> str:
        return f"%{self.id} = {self.__class__.__name__} %{context.tvc[self.type]} %{self.operand.id}"


class BinaryLogicalOperator(LogicalOperator[T, Optional[S]]):
    type: Type = None
    operand1: Union[Statement, Constant] = None
    operand2: Union[Statement, Constant] = None

    def to_spasm(self, context: "Context") -> str:
        return f"%{self.id} = {self.__class__.__name__} %{context.tvc[self.type]} %{self.operand1.id} %{self.operand2.id}"


# class OpAny(UnaryLogicalOperatorFuzzMixin, UnaryLogicalOperator[OpTypeBool]):
#     ...

# class OpAll(UnaryLogicalOperatorFuzzMixin, UnaryLogicalOperator[OpTypeBool]):
#     ...


class OpLogicalEqual(
    BinaryLogicalOperatorFuzzMixin, BinaryLogicalOperator[OpTypeBool, None]
):
    ...


class OpLogicalNotEqual(
    BinaryLogicalOperatorFuzzMixin, BinaryLogicalOperator[OpTypeBool, None]
):
    ...


class OpLogicalOr(
    BinaryLogicalOperatorFuzzMixin, BinaryLogicalOperator[OpTypeBool, None]
):
    ...


class OpLogicalAnd(
    BinaryLogicalOperatorFuzzMixin, BinaryLogicalOperator[OpTypeBool, None]
):
    ...


class OpLogicalNot(
    UnaryLogicalOperatorFuzzMixin, UnaryLogicalOperator[OpTypeBool, None]
):
    ...


class OpIEqual(BinaryLogicalOperatorFuzzMixin, BinaryLogicalOperator[OpTypeInt, None]):
    ...


class OpINotEqual(
    BinaryLogicalOperatorFuzzMixin, BinaryLogicalOperator[OpTypeInt, None]
):
    ...


class OpUGreaterThan(
    BinaryLogicalOperatorFuzzMixin, BinaryLogicalOperator[OpTypeInt, Unsigned]
):
    ...

class OpSGreaterThan(
    BinaryLogicalOperatorFuzzMixin, BinaryLogicalOperator[OpTypeInt, Signed]
):
    ...

class OpUGreaterThanEqual(
    BinaryLogicalOperatorFuzzMixin, BinaryLogicalOperator[OpTypeInt, Unsigned]
):
    ...
    
class OpSGreaterThanEqual(
    BinaryLogicalOperatorFuzzMixin, BinaryLogicalOperator[OpTypeInt, Signed]
):
    ...
    
class OpULessThan(
    BinaryLogicalOperatorFuzzMixin, BinaryLogicalOperator[OpTypeInt, Unsigned]
):
    ...

class OpSLessThan(
    BinaryLogicalOperatorFuzzMixin, BinaryLogicalOperator[OpTypeInt, Signed]
):
    ...

class OpULessThanEqual(
    BinaryLogicalOperatorFuzzMixin, BinaryLogicalOperator[OpTypeInt, Unsigned]
):
    ...

class OpSLessThanEqual(
    BinaryLogicalOperatorFuzzMixin, BinaryLogicalOperator[OpTypeInt, Signed]
):
    ...

class OpFOrdEqual(BinaryLogicalOperatorFuzzMixin, BinaryLogicalOperator[OpTypeFloat, None]):
    ...

class OpFUnordEqual(BinaryLogicalOperatorFuzzMixin, BinaryLogicalOperator[OpTypeFloat, None]):
    ...

class OpFOrdNotEqual(BinaryLogicalOperatorFuzzMixin, BinaryLogicalOperator[OpTypeFloat, None]):
    ...

class OpFUnordNotEqual(BinaryLogicalOperatorFuzzMixin, BinaryLogicalOperator[OpTypeFloat, None]):
    ...

class OpFOrdLessThan(BinaryLogicalOperatorFuzzMixin, BinaryLogicalOperator[OpTypeFloat, None]):
    ...

class OpFUnordLessThan(BinaryLogicalOperatorFuzzMixin, BinaryLogicalOperator[OpTypeFloat, None]):
    ...

class OpFOrdGreaterThan(BinaryLogicalOperatorFuzzMixin, BinaryLogicalOperator[OpTypeFloat, None]):
    ...

class OpFUnordGreaterThan(BinaryLogicalOperatorFuzzMixin, BinaryLogicalOperator[OpTypeFloat, None]):
    ...

class OpFOrdLessThanEqual(BinaryLogicalOperatorFuzzMixin, BinaryLogicalOperator[OpTypeFloat, None]):
    ...

class OpFUnordLessThanEqual(BinaryLogicalOperatorFuzzMixin, BinaryLogicalOperator[OpTypeFloat, None]):
    ...

class OpFOrdGreaterThanEqual(BinaryLogicalOperatorFuzzMixin, BinaryLogicalOperator[OpTypeFloat, None]):
    ...

class OpFUnordGreaterThanEqual(BinaryLogicalOperatorFuzzMixin, BinaryLogicalOperator[OpTypeFloat, None]):
    ...
