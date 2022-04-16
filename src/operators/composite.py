import random
from typing import TYPE_CHECKING
from src import OpCode, Statement, Type
from src.operators import Operand
from src.predicates import (
    HasValidBaseTypeAndSign,
    HasValidTypeAndSign,
    IsArrayType,
    IsCompositeType,
    IsMatrixType,
    IsScalarInteger,
    IsStructType,
    IsVectorType,
)
from src.types.concrete_types import OpTypeMatrix, OpTypeVector

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


# class OpVectorShuffle(CompositeOperator):
#     type: Type = None
#     vector1: Statement = None
#     vector2: Statement = None
#     indices: Statement = None

#     def fuzz(self, context: "Context") -> list[OpCode]:
#         vector1 = context.get_random_operand(IsVectorType)
#         if vector1 is None:
#             return []
#         signedness = None
#         if hasattr(vector1.get_base_type(), "signed"):
#             signedness = vector1.get_base_type().signed
#         vector2 = context.get_random_operand(
#             lambda x: IsVectorType(x)
#             and HasValidBaseTypeAndSign(x, vector1.get_base_type(), signedness)
#         )
#         if vector2 is None:
#             return []
#         # indices = ???
#         self.type = vector1.type
#         self.vector1 = vector1
#         self.vector2 = vector2
#         self.indices = indices
#         return [self]

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
            signedness = None
            if hasattr(composite.get_base_type(), "signed"):
                signedness = composite.get_base_type().signed
            object = context.get_random_operand(
                lambda x: HasValidTypeAndSign(
                    x, composite.get_base_type().__class__, signedness
                )
            )
        else:
            indexes = (random.SystemRandom().randint(0, len(composite.type) - 1),)
            target_type = (
                composite.type.types[indexes[0]]
                if IsStructType(composite)
                else composite.get_base_type()
            )
            signedness = None
            if hasattr(target_type, "signed"):
                signedness = target_type.signed
            object = context.get_random_operand(
                lambda x: HasValidTypeAndSign(x, target_type.__class__, signedness)
            )
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
