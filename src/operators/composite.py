import random
from math import ceil
from math import log2
from typing import TYPE_CHECKING

from typing_extensions import Self

from src import FuzzResult
from src import Statement
from src.operators import Operand
from src.patched_dataclass import dataclass
from src.predicates import And
from src.predicates import HasBaseType
from src.predicates import HasType
from src.predicates import IsCompositeType
from src.predicates import IsMatrixType
from src.predicates import IsScalarInteger
from src.predicates import IsStructType
from src.predicates import IsVectorType
from src.types.concrete_types import OpTypeMatrix
from src.types.concrete_types import OpTypeVector

if TYPE_CHECKING:
    from src.context import Context


@dataclass
class CompositeOperator(Statement):
    ...


@dataclass
class OpVectorExtractDynamic(CompositeOperator):
    vector: Operand
    index: Operand

    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        vector = context.get_random_operand(IsVectorType)
        index = context.get_random_operand(IsScalarInteger)
        return FuzzResult(cls(type=vector.get_base_type(), vector=vector, index=index))


@dataclass
class OpVectorInsertDynamic(CompositeOperator):
    vector: Operand
    component: Operand
    index: Operand

    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        vector = context.get_random_operand(IsVectorType)
        component = context.get_random_operand(HasType(vector.get_base_type()))
        return FuzzResult(
            cls(
                type=vector.type,
                vector=vector,
                component=component,
                index=context.get_random_operand(IsScalarInteger),
            )
        )


@dataclass
class OpVectorShuffle(CompositeOperator):
    vector1: Operand
    vector2: Operand
    components: tuple[int, ...]

    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        vector1 = context.get_random_operand(IsVectorType)
        vector2 = context.get_random_operand(
            And(IsVectorType, HasBaseType(vector1.get_base_type()))
        )

        inner_type = OpTypeVector(
            type=vector1.get_base_type(),
            size=min(4, 2 ** (ceil(log2(len(vector1.type) + len(vector2.type))))),
        )
        context.add_to_tvc(inner_type)
        components = tuple(
            [
                context.rng.randint(0, len(inner_type) - 1)
                for _ in range(len(inner_type))
            ]
        )
        return FuzzResult(
            cls(
                type=inner_type, vector1=vector1, vector2=vector2, components=components
            )
        )


# class OpCompositeConstruct:
#     ...


@dataclass
class OpCompositeExtract(CompositeOperator):
    composite: Operand
    indexes: tuple[int, ...]

    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        composite: Operand = context.get_random_operand(IsCompositeType)
        if IsMatrixType(composite):
            indexes = (
                context.rng.randint(0, len(composite.type) - 1),
                context.rng.randint(0, len(composite.type.type) - 1),
            )
            inner_type = composite.get_base_type()
        else:
            indexes = (context.rng.randint(0, len(composite.type) - 1),)
            inner_type = (
                composite.type.types[indexes[0]]
                if IsStructType(composite)
                else composite.get_base_type()
            )
        return FuzzResult(cls(type=inner_type, composite=composite, indexes=indexes))


@dataclass
class OpCompositeInsert(CompositeOperator):
    object: Operand
    composite: Operand
    indexes: tuple[int, ...]

    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        composite = context.get_random_operand(IsCompositeType)
        if IsMatrixType(composite):
            indexes = (
                context.rng.randint(0, len(composite.type) - 1),
                context.rng.randint(0, len(composite.type.type) - 1),
            )
            target_object = context.get_random_operand(
                HasType(composite.get_base_type())
            )
        else:
            indexes = (context.rng.randint(0, len(composite.type) - 1),)
            target_type = (
                composite.type.types[indexes[0]]
                if IsStructType(composite)
                else composite.get_base_type()
            )
            target_object = context.get_random_operand(HasType(target_type))
        return FuzzResult(
            cls(
                type=composite.type,
                object=target_object,
                composite=composite,
                indexes=indexes,
            )
        )


@dataclass
class OpCopyObject(CompositeOperator):
    object: Operand

    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        target_object = context.get_random_operand(lambda _: True)
        return FuzzResult(cls(type=target_object.type, object=target_object))


@dataclass
class OpTranspose(CompositeOperator):
    object: Operand

    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        target_object = context.get_random_operand(IsMatrixType)
        inner_type = OpTypeMatrix(
            type=OpTypeVector(
                type=target_object.get_base_type(), size=len(target_object.type)
            ),
            size=len(target_object.type.type),
        )
        context.add_to_tvc(inner_type.type)
        context.add_to_tvc(inner_type)
        return FuzzResult(cls(type=inner_type, object=target_object))
