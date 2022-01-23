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
    ArithmeticType,
    NumericalType,
    ScalarType,
)
from langspec.opcodes.types.concrete_types import (
    OpTypeFloat,
    OpTypeInt,
    OpTypeVector,
    Type,
)


def find_arithmetic_operands(
    context: "Context", target_type: Type
) -> Tuple[Union[Statement, Constant], Union[Statement, Constant]]:
    operands: List[Statement] = (
        context.get_arithmetic_statements() + context.get_arithmetic_constants()
    )
    eligible_operands: List[Union[Statement, Constant]] = []
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


class UnaryArithmeticOperator(Statement, Generic[T]):
    type: Type = None
    operand: Union[Statement, Constant] = None

    def fuzz(self, context: "Context") -> List[OpCode]:
        target_type = get_args(self.__class__.__orig_bases__[0])
        operands = find_arithmetic_operands(context, target_type)
        if not operands:
            return []
        self.operand: Statement = operands[0]
        self.type = self.operand.type
        return [self]


class BinaryArithmeticOperator(Statement, Generic[T]):
    type: Type = None
    operand1: Union[Statement, Constant] = None
    operand2: Union[Statement, Constant] = None

    def fuzz(self, context: "Context") -> List[OpCode]:
        target_type = get_args(self.__class__.__orig_bases__[0])
        operands = find_arithmetic_operands(context, target_type)
        if not operands:
            return []
        self.operand1 = operands[0]
        self.operand2 = operands[1]
        self.type = self.operand1.type
        return [self]


class OpSNegate(UnaryArithmeticOperator[OpTypeInt]):
    pass


class OpFNegate(UnaryArithmeticOperator[OpTypeFloat]):
    pass


class OpIAdd(BinaryArithmeticOperator[OpTypeInt]):
    pass


class OpFAdd(BinaryArithmeticOperator[OpTypeFloat]):
    pass


class OpISub(BinaryArithmeticOperator[OpTypeInt]):
    pass


class OpFSub(BinaryArithmeticOperator[OpTypeFloat]):
    pass


class OpIMul(BinaryArithmeticOperator[OpTypeInt]):
    pass


class OpFMul(BinaryArithmeticOperator[OpTypeFloat]):
    pass


# class OpUDiv(BinaryArithmeticOperator[OpTypeFloat]):
#     pass

# class OpSDiv(BinaryArithmeticOperator[OpTypeFloat]):
#     pass


class OpFMul(BinaryArithmeticOperator[OpTypeFloat]):
    pass


class OpFMod(BinaryArithmeticOperator[OpTypeFloat]):
    pass


class OpFRem(BinaryArithmeticOperator[OpTypeFloat]):
    pass
