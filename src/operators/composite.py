from math import ceil, log2
import random
from typing import TYPE_CHECKING
from src import OpCode, Statement, Type
from src.operators import Operand
from src.predicates import (
    And,
    HasBaseType,
    HasType,
    IsCompositeType,
    IsMatrixType,
    IsScalarInteger,
    IsStructType,
    IsVectorType,
)
from src.types.concrete_types import OpTypeInt, OpTypeMatrix, OpTypeStruct, OpTypeVector

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
        component = context.get_random_operand(HasType(vector.get_base_type()))
        if component is None:
            return []
        self.type = vector.type
        self.vector = vector
        self.component = component
        self.index = context.get_random_operand(IsScalarInteger)
        return [self]


class OpVectorShuffle(CompositeOperator):
    type: Type = None
    vector1: Statement = None
    vector2: Statement = None
    components: tuple[int] = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        vector1 = context.get_random_operand(IsVectorType)
        if vector1 is None:
            return []
        vector2 = context.get_random_operand(
            And(IsVectorType, HasBaseType(vector1.get_base_type()))
        )
        if vector2 is None:
            return []

        self.type = OpTypeVector()
        self.type.type = vector1.get_base_type()
        self.type.size = min(
            4, 2 ** (ceil(log2(len(vector1.type) + len(vector2.type))))
        )
        context.add_to_tvc(self.type)
        self.vector1 = vector1
        self.vector2 = vector2
        self.components = tuple(
            [
                random.SystemRandom().randint(0, self.type.size - 1)
                for _ in range(self.type.size)
            ]
        )
        return [self]


# class OpCompositeConstruct:
#     ...


class OpCompositeExtract(CompositeOperator):
    type: Type = None
    composite: Operand = None
    indexes: tuple[int] = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        composite = context.get_random_operand(IsCompositeType)
        if composite is None:
            return []
        if IsMatrixType(composite):
            indexes = (
                random.SystemRandom().randint(0, len(composite.type) - 1),
                random.SystemRandom().randint(0, len(composite.type.type) - 1),
            )
            type = composite.get_base_type()
        else:
            indexes = (random.SystemRandom().randint(0, len(composite.type) - 1),)
            type = (
                composite.type.types[indexes[0]]
                if IsStructType(composite)
                else composite.get_base_type()
            )
        self.type = type
        self.composite = composite
        self.indexes = indexes
        return [self]


class OpCompositeInsert(CompositeOperator):
    type: Type = None
    object: Statement = None
    composite: Statement = None
    indexes: tuple[int] = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        composite = context.get_random_operand(IsCompositeType)
        if composite is None:
            return []
        if IsMatrixType(composite):
            indexes = (
                random.SystemRandom().randint(0, len(composite.type) - 1),
                random.SystemRandom().randint(0, len(composite.type.type) - 1),
            )
            object = context.get_random_operand(HasType(composite.get_base_type()))
        else:
            indexes = (random.SystemRandom().randint(0, len(composite.type) - 1),)
            target_type = (
                composite.type.types[indexes[0]]
                if IsStructType(composite)
                else composite.get_base_type()
            )
            object = context.get_random_operand(HasType(target_type))
        self.type = composite.type
        self.object = object
        self.composite = composite
        self.indexes = indexes
        return [self]


class OpCopyObject(CompositeOperator):
    type: Type = None
    object: Statement = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        object = context.get_random_operand(lambda _: True)
        if object is None:
            return []
        self.type = object.type
        self.object = object
        return [self]


class OpTranspose(CompositeOperator):
    type: Type = None
    object: Statement = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        object = context.get_random_operand(IsMatrixType)
        if object is None:
            return []
        self.type = OpTypeMatrix()
        self.type.type = OpTypeVector()
        self.type.type.type = object.get_base_type()
        self.type.type.size = len(object.type)
        self.type.size = len(object.type.type)
        context.add_to_tvc(self.type.type)
        context.add_to_tvc(self.type)
        self.object = object
        return [self]
