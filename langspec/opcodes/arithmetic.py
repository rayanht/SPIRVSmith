import random
from typing import (
    TYPE_CHECKING,
    Generic,
    List,
    Tuple,
    TypeVar,
    Union,
    get_args,
)
from langspec.opcodes import OpCode, Statement

from langspec.opcodes.constants import Constant

if TYPE_CHECKING:
    from langspec.opcodes.context import Context
from langspec.opcodes.types.abstract_types import (
    NumericalType,
)
from langspec.opcodes.types.concrete_types import (
    OpTypeFloat,
    OpTypeInt,
    OpTypeVector,
    Type,
)

Operand = Statement | Constant

def find_arithmetic_operands(
    context: "Context", target_type: Type
) -> Tuple[Operand, Operand]:
    operands: List[Statement] = (
        context.get_arithmetic_statements() + context.get_arithmetic_constants()
    )
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
                filter(lambda op: isinstance(op.type, OpTypeVector), eligible_operands)
            )
        )
    elif isinstance(operand1.type, NumericalType):
        operand2 = random.choice(
            list(
                filter(lambda op: isinstance(op.type, NumericalType), eligible_operands)
            )
        )
    return operand1, operand2


T = TypeVar("T")

class ArithmeticOperator(Statement, Generic[T]):
    pass

class UnaryArithmeticOperatorFuzzMixin:
    def fuzz(self, context: "Context") -> List[OpCode]:
        target_type = get_args(self.__class__.__orig_bases__[1])
        operands = find_arithmetic_operands(context, target_type)
        if not operands:
            return []
        self.operand: Statement = operands[0]
        self.type = self.operand.type
        return [self]


class BinaryArithmeticOperatorFuzzMixin:
    def fuzz(self, context: "Context") -> List[OpCode]:
        target_type = get_args(self.__class__.__orig_bases__[1])
        operands = find_arithmetic_operands(context, target_type)
        if not operands:
            return []
        self.operand1 = operands[0]
        self.operand2 = operands[1]
        self.type = self.operand1.type
        return [self]


class UnaryArithmeticOperator(ArithmeticOperator[T]):
    type: Type = None
    operand: Operand = None
    
    def to_spasm(self, context: "Context") -> str:
        return f"%{self.id} = {self.__class__.__name__} %{context.tvc[self.type]} %{self.operand.id}"


class BinaryArithmeticOperator(ArithmeticOperator[T]):
    type: Type = None
    operand1: Operand = None
    operand2: Operand = None
    
    def to_spasm(self, context: "Context") -> str:
        return f"%{self.id} = {self.__class__.__name__} %{context.tvc[self.type]} %{self.operand1.id} %{self.operand2.id}"


class OpSNegate(UnaryArithmeticOperatorFuzzMixin, UnaryArithmeticOperator[OpTypeInt]):
    pass


class OpFNegate(UnaryArithmeticOperatorFuzzMixin, UnaryArithmeticOperator[OpTypeFloat]):
    pass


class OpIAdd(BinaryArithmeticOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeInt]):
    pass


class OpFAdd(BinaryArithmeticOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeFloat]):
    pass


class OpISub(BinaryArithmeticOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeInt]):
    pass


class OpFSub(BinaryArithmeticOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeFloat]):
    pass


class OpIMul(BinaryArithmeticOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeInt]):
    pass


class OpFMul(BinaryArithmeticOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeFloat]):
    pass


# class OpUDiv(BinaryArithmeticOperator[OpTypeFloat]):
#     pass

# class OpSDiv(BinaryArithmeticOperator[OpTypeFloat]):
#     pass


class OpFMod(BinaryArithmeticOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeFloat]):
    pass


class OpFRem(BinaryArithmeticOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeFloat]):
    pass
