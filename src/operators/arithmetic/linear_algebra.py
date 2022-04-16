from typing import (
    TYPE_CHECKING,
)
from src import OpCode
from src.operators import Operand
from src.operators.arithmetic import BinaryArithmeticOperator


if TYPE_CHECKING:
    from src.context import Context
from src.predicates import (
    And,
    HasBaseType,
    HasFloatBaseType,
    HasLength,
    HasValidBaseType,
    HaveSameTypeLength,
    IsMatrixType,
    IsScalarFloat,
    IsVectorType,
)

from src.types.concrete_types import (
    OpTypeFloat,
    OpTypeMatrix,
    OpTypeVector,
)


# The following operators override the fuzzing logic rather than relying on the mixin
# This is because trying to encompass their logic in the mixin would be way too complex:


class OpVectorTimesScalar(BinaryArithmeticOperator[None, None, None, None]):
    type: OpTypeVector = None
    operand1: Operand = None
    operand2: Operand = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        operand1 = context.get_random_operand(And(IsVectorType, HasFloatBaseType))
        if not operand1:
            return []
        operand2 = context.get_random_operand(IsScalarFloat)
        if not operand2:
            return []
        self.type = operand1.type
        self.operand1 = operand1
        self.operand2 = operand2
        return [self]


class OpMatrixTimesScalar(BinaryArithmeticOperator[None, None, None, None]):
    type: OpTypeMatrix = None
    operand1: Operand = None
    operand2: Operand = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        operand1 = context.get_random_operand(And(IsMatrixType, HasFloatBaseType))
        if not operand1:
            return []
        operand2 = context.get_random_operand(IsScalarFloat)
        if not operand2:
            return []
        self.type = operand1.type
        self.operand1 = operand1
        self.operand2 = operand2
        return [self]


class OpVectorTimesMatrix(BinaryArithmeticOperator[None, None, None, None]):
    type: OpTypeVector = None
    operand1: Operand = None
    operand2: Operand = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        # We pick the matrix first here because we tend to have more vectors than matrices
        operand2 = context.get_random_operand(And(IsMatrixType, HasFloatBaseType))
        if not operand2:
            return []
        # The vector must have as many element as the matrix has rows
        operand1 = context.get_random_operand(
            And(IsVectorType, HasFloatBaseType, HasLength(len(operand2.type.type)))
        )
        if not operand1:
            return []
        self.type = OpTypeVector()
        self.type.type = operand1.get_base_type()
        self.type.size = len(operand2.type)
        context.add_to_tvc(self.type)
        self.operand1 = operand1
        self.operand2 = operand2
        return [self]


class OpMatrixTimesVector(BinaryArithmeticOperator[None, None, None, None]):
    type: OpTypeVector = None
    operand1: Operand = None
    operand2: Operand = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        operand1 = context.get_random_operand(And(IsMatrixType, HasFloatBaseType))
        if not operand1:
            return []
        # The vector must have as many elements as the matrix has columns
        operand2 = context.get_random_operand(
            And(IsVectorType, HasFloatBaseType, HasLength(len(operand1.type)))
        )
        if not operand2:
            return []
        self.type = OpTypeVector()
        self.type.type = operand1.get_base_type()
        self.type.size = len(operand1.type.type)
        context.add_to_tvc(self.type)
        self.operand1 = operand1
        self.operand2 = operand2
        return [self]


class OpMatrixTimesMatrix(BinaryArithmeticOperator[None, None, None, None]):
    type: OpTypeMatrix = None
    operand1: Operand = None
    operand2: Operand = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        operand1 = context.get_random_operand(And(IsMatrixType, HasFloatBaseType))
        if not operand1:
            return []
        # operand2 must have the same number of columns that operand1 has
        # rows, tricky case if we got unlucky and picked for operand1
        # a matrix that could be multiplied by operand2 in the symmetric case
        #
        # e.g. we picked a mat2x4 for operand1 and the only other matrix
        # in scope is a mat3x2. We can't multiply them together, but we can
        # swap them around to resolve this.
        operand2 = context.get_random_operand(
            lambda x: (IsMatrixType(x) and HasFloatBaseType(x))
            and (
                #     len(x.type.type) == len(operand1.type)
                # <=> # rows of operand2 == # columns of operand1
                # <=> the trivial case
                HaveSameTypeLength(x.type, operand1)
                #     len(x.type) == len(operand1.type.type)
                # <=> # columns of operand2 == # rows of operand1
                # <=> the symmetric case
                or HaveSameTypeLength(x, operand1.type)
            )
        )
        if not operand2:
            return []

        # Handle the symmetric case
        #     len(operand1.type) != len(operand2.type.type)
        # <=> # columns of operand1 != # rows of operand2
        # <=> the symmetric case
        if len(operand1.type) != len(operand2.type.type):
            operand1, operand2 = operand2, operand1

        # The resulting matrix has the same number of rows as operand1
        # and same number of columns as operand2
        self.type = OpTypeMatrix()
        # Rows
        self.type.type = operand1.type.type
        # Columns
        self.type.size = len(operand2.type)
        context.add_to_tvc(self.type)
        self.operand1 = operand1
        self.operand2 = operand2
        return [self]


class OpOuterProduct(BinaryArithmeticOperator[None, None, None, None]):
    type: OpTypeMatrix = None
    operand1: Operand = None
    operand2: Operand = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        operand1 = context.get_random_operand(And(IsVectorType, HasFloatBaseType))
        if not operand1:
            return []
        operand2 = context.get_random_operand(And(IsVectorType, HasFloatBaseType))
        self.type = OpTypeMatrix()
        self.type.type = operand1.type
        self.type.size = len(operand2.type)
        context.add_to_tvc(self.type)
        self.operand1 = operand1
        self.operand2 = operand2
        return [self]


class OpDot(BinaryArithmeticOperator[None, None, None, None]):
    type: OpTypeFloat = None
    operand1: Operand = None
    operand2: Operand = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        operand1 = context.get_random_operand(And(IsVectorType, HasFloatBaseType))
        if not operand1:
            return []
        operand2 = context.get_random_operand(
            And(
                IsVectorType,
                HasBaseType(operand1.get_base_type()),
                HasLength(len(operand1.type)),
            )
        )
        self.type = operand1.get_base_type()
        self.operand1 = operand1
        self.operand2 = operand2
        return [self]
