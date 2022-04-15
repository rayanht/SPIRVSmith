from typing import TYPE_CHECKING
from src import OpCode, Statement, Type
from src.predicates import (
    HasValidTypeAndSign,
    IsScalarInteger,
    IsVectorType,
)

if TYPE_CHECKING:
    from src.context import Context


class CompositeOperator(Statement):
    ...


class OpVectorExtractDynamic(CompositeOperator):
    type: Type = None
    vector: Statement = None
    index: Statement = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        vector = context.get_random_operand(IsVectorType)
        if vector is None:
            return []

        self.type = vector.get_base_type()
        self.vector = vector
        self.index = context.get_random_operand(IsScalarInteger)
        return [self]


class OpVectorInsertDynamic(CompositeOperator):
    type: Type = None
    vector: Statement = None
    component: Statement = None
    index: Statement = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        vector = context.get_random_operand(IsVectorType)
        if vector is None:
            return []
        base_type = vector.get_base_type()
        signedness = None
        if hasattr(base_type, "signed"):
            signedness = base_type.signed
        component = context.get_random_operand(
            lambda x: HasValidTypeAndSign(x, base_type.__class__, signedness)
        )
        if component is None:
            return []
        self.type = vector.type
        self.vector = vector
        self.component = component
        self.index = context.get_random_operand(IsScalarInteger)
        return [self]
