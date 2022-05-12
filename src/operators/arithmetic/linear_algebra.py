from typing import (
    TYPE_CHECKING,
)

from typing_extensions import Self

from src import FuzzResult
from src.operators.arithmetic import BinaryArithmeticOperator
from src.patched_dataclass import dataclass

if TYPE_CHECKING:
    from src.context import Context
from src.predicates import (
    And,
    HasBaseType,
    IsOfFloatBaseType,
    HasLength,
    HaveSameTypeLength,
    IsMatrixType,
    IsScalarFloat,
    IsVectorType,
)

from src.types.concrete_types import (
    OpTypeMatrix,
    OpTypeVector,
)


# The following operators override the fuzzing logic rather than relying on the mixin
# This is because trying to encompass their logic in the mixin would be way too complex:


@dataclass
class OpVectorTimesScalar(BinaryArithmeticOperator[None, None, None, None]):
    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        operand1 = context.get_random_operand(And(IsVectorType, IsOfFloatBaseType))
        operand2 = context.get_random_operand(IsScalarFloat)
        return FuzzResult(cls(type=operand1.type, operand1=operand1, operand2=operand2))


@dataclass
class OpMatrixTimesScalar(BinaryArithmeticOperator[None, None, None, None]):
    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        operand1 = context.get_random_operand(And(IsMatrixType, IsOfFloatBaseType))
        operand2 = context.get_random_operand(IsScalarFloat)
        return FuzzResult(cls(type=operand1.type, operand1=operand1, operand2=operand2))


@dataclass
class OpVectorTimesMatrix(BinaryArithmeticOperator[None, None, None, None]):
    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        # We pick the matrix first here because we tend to have more vectors than matrices
        operand2 = context.get_random_operand(And(IsMatrixType, IsOfFloatBaseType))
        # The vector must have as many element as the matrix has rows
        operand1 = context.get_random_operand(
            And(IsVectorType, IsOfFloatBaseType, HasLength(len(operand2.type.type)))
        )
        result_type = OpTypeVector(
            type=operand1.get_base_type(), size=len(operand2.type)
        )
        return FuzzResult(
            cls(type=result_type, operand1=operand1, operand2=operand2), [result_type]
        )


@dataclass
class OpMatrixTimesVector(BinaryArithmeticOperator[None, None, None, None]):
    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        operand1 = context.get_random_operand(And(IsMatrixType, IsOfFloatBaseType))
        # The vector must have as many elements as the matrix has columns
        operand2 = context.get_random_operand(
            And(IsVectorType, IsOfFloatBaseType, HasLength(len(operand1.type)))
        )
        result_type = OpTypeVector(
            type=operand1.get_base_type(), size=len(operand1.type.type)
        )
        return FuzzResult(
            cls(type=result_type, operand1=operand1, operand2=operand2), [result_type]
        )


@dataclass
class OpMatrixTimesMatrix(BinaryArithmeticOperator[None, None, None, None]):
    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        operand1 = context.get_random_operand(And(IsMatrixType, IsOfFloatBaseType))
        # operand2 must have the same number of columns that operand1 has
        # rows, tricky case if we got unlucky and picked for operand1
        # a matrix that could be multiplied by operand2 in the symmetric case
        #
        # e.g. we picked a mat2x4 for operand1 and the only other matrix
        # in scope is a mat3x2. We can't multiply them together, but we can
        # swap them around to resolve this.
        operand2 = context.get_random_operand(
            lambda x: (IsMatrixType(x) and IsOfFloatBaseType(x))
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

        # Handle the symmetric case
        #     len(operand1.type) != len(operand2.type.type)
        # <=> # columns of operand1 != # rows of operand2
        # <=> the symmetric case
        if len(operand1.type) != len(operand2.type.type):
            operand1, operand2 = operand2, operand1

        # The resulting matrix has the same number of rows as operand1
        # and same number of columns as operand2
        result_type = OpTypeMatrix(type=operand1.type.type, size=len(operand2.type))
        return FuzzResult(
            cls(type=result_type, operand1=operand1, operand2=operand2), [result_type]
        )


@dataclass
class OpOuterProduct(BinaryArithmeticOperator[None, None, None, None]):
    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        operand1 = context.get_random_operand(And(IsVectorType, IsOfFloatBaseType))
        operand2 = context.get_random_operand(And(IsVectorType, IsOfFloatBaseType))
        result_type = OpTypeMatrix(type=operand1.type, size=len(operand2.type))
        return FuzzResult(
            cls(type=result_type, operand1=operand1, operand2=operand2), [result_type]
        )


@dataclass
class OpDot(BinaryArithmeticOperator[None, None, None, None]):
    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        operand1 = context.get_random_operand(And(IsVectorType, IsOfFloatBaseType))
        operand2 = context.get_random_operand(
            And(
                IsVectorType,
                HasBaseType(operand1.get_base_type()),
                HasLength(len(operand1.type)),
            )
        )
        return FuzzResult(
            cls(type=operand1.get_base_type(), operand1=operand1, operand2=operand2)
        )
