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

Operand = Statement | Constant

def find_bitwise_operands(
    context: "Context", target_type: Type
) -> Tuple[Operand, Operand]:
    operands: List[Statement] = context.get_typed_statements(
        lambda _: True
    ) + context.get_constants((OpTypeInt, OpTypeVector))
    eligible_operands: List[Operand] = []
    for operand in operands:
        if isinstance(operand.type, target_type) or (
            isinstance(operand.type, OpTypeVector)
            and isinstance(operand.type.type, target_type)
        ):
            eligible_operands.append(operand)
    if len(eligible_operands) == 0:
        return None
    operand1 = random.choice(eligible_operands)
    if isinstance(operand1.type, OpTypeVector):
        operand2 = random.choice(
            list(
                filter(
                    lambda op: isinstance(op.type, OpTypeVector)
                    and op.type.size == operand1.type.size,
                    eligible_operands,
                )
            )
        )
    elif isinstance(operand1.type, OpTypeInt):
        operand2 = random.choice(
            list(filter(lambda op: isinstance(op.type, OpTypeInt), eligible_operands))
        )
    return operand1, operand2


T = TypeVar("T")


class BitwiseOperator(Statement, Generic[T]):
    pass


class UnaryBitwiseOperatorFuzzMixin:
    def fuzz(self, context: "Context") -> List[OpCode]:
        target_type = get_args(self.__class__.__orig_bases__[1])
        operands = find_bitwise_operands(context, target_type)
        if not operands:
            return []
        self.operand: Statement = operands[0]
        self.type = self.operand.type
        return [self]


class BinaryBitwiseOperatorFuzzMixin:
    def fuzz(self, context: "Context") -> List[OpCode]:
        target_type = get_args(self.__class__.__orig_bases__[1])
        operands = find_bitwise_operands(context, target_type)
        if not operands:
            return []
        self.operand1 = operands[0]
        self.operand2 = operands[1]
        self.type = self.operand1.type
        return [self]


class UnaryBitwiseOperator(BitwiseOperator[T]):
    type: Type = None
    operand: Operand = None

    def to_spasm(self, context: "Context") -> str:
        return f"%{self.id} = {self.__class__.__name__} %{context.tvc[self.type]} %{self.operand.id}"


class BinaryBitwiseOperator(BitwiseOperator[T]):
    type: Type = None
    operand1: Operand = None
    operand2: Operand = None

    def to_spasm(self, context: "Context") -> str:
        return f"%{self.id} = {self.__class__.__name__} %{context.tvc[self.type]} %{self.operand1.id} %{self.operand2.id}"


class OpShiftRightLogical(BinaryBitwiseOperatorFuzzMixin, BinaryBitwiseOperator[OpTypeInt]):
    ...
    
class OpShiftRightArithmetic(BinaryBitwiseOperatorFuzzMixin, BinaryBitwiseOperator[OpTypeInt]):
    ...

class OpShiftLeftLogical(BinaryBitwiseOperatorFuzzMixin, BinaryBitwiseOperator[OpTypeInt]):
    ...

class OpBitwiseOr(BinaryBitwiseOperatorFuzzMixin, BinaryBitwiseOperator[OpTypeInt]):
    ...

class OpBitwiseXor(BinaryBitwiseOperatorFuzzMixin, BinaryBitwiseOperator[OpTypeInt]):
    ...

class OpBitwiseAnd(BinaryBitwiseOperatorFuzzMixin, BinaryBitwiseOperator[OpTypeInt]):
    ...

class OpNot(UnaryBitwiseOperatorFuzzMixin, UnaryBitwiseOperator[OpTypeInt]):
    ...

class OpBitCount(UnaryBitwiseOperatorFuzzMixin, UnaryBitwiseOperator[OpTypeInt]):
    ...
