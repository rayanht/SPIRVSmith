import random
from dataclasses import field
from typing import Callable
from typing import TYPE_CHECKING

from typing_extensions import Self

from src.constants import OpConstant
from src.operators import Operand
from src.operators.memory import MemoryOperator
from src.operators.memory.variable import OpVariable
from src.patched_dataclass import dataclass
from src.predicates import HasType
from src.predicates import IsCompositeType
from src.predicates import IsMatrixType
from src.predicates import IsOutputVariable
from src.predicates import IsPointerType
from src.predicates import IsStructType
from src.predicates import Not

if TYPE_CHECKING:
    from src.context import Context
from src import (
    AbortFuzzing,
    FuzzResult,
    OpCode,
    Statement,
    Untyped,
    VoidOp,
)
from src.types.concrete_types import (
    EmptyType,
    OpTypeInt,
    OpTypePointer,
    Type,
)


@dataclass
class OpLoad(MemoryOperator):
    variable: OpVariable
    # memory_operands: Optional[???]

    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        variable: OpVariable = random.SystemRandom().choice(
            list(
                filter(
                    Not(IsOutputVariable),
                    context.get_local_variables() + context.get_global_variables(),
                )
            )
        )
        return FuzzResult(cls(type=variable.type.type, variable=variable))


@dataclass
class OpStore(MemoryOperator, Untyped, VoidOp):
    pointer: OpTypePointer
    object: OpCode
    # memory_operands: Optional[???]

    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        pointer: OpTypePointer = context.get_random_operand(IsPointerType)
        target_object: Operand = context.get_random_operand(HasType(pointer.type.type))
        return FuzzResult(cls(type=EmptyType(), pointer=pointer, object=target_object))


@dataclass
class OpAccessChain(MemoryOperator):
    base: OpVariable
    indexes: tuple[OpConstant, ...]

    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        predicate: Callable[[OpVariable], bool] = lambda var: IsCompositeType(var.type)
        base: OpVariable = random.SystemRandom().choice(
            list(filter(predicate, context.get_storage_buffers()))
        )
        if base is None:
            raise AbortFuzzing
        composite_pointer = base.type
        if IsMatrixType(composite_pointer):
            indexes = (
                random.SystemRandom().randint(0, len(composite_pointer.type) - 1),
                random.SystemRandom().randint(0, len(composite_pointer.type.type) - 1),
            )
            pointer_inner_type = composite_pointer.get_base_type()
        else:
            indexes = (
                random.SystemRandom().randint(0, len(composite_pointer.type) - 1),
            )
            pointer_inner_type = (
                composite_pointer.type.types[indexes[0]]
                if IsStructType(composite_pointer)
                else composite_pointer.get_base_type()
            )
        pointer_type = OpTypePointer(
            storage_class=base.storage_class, type=pointer_inner_type
        )
        context.add_to_tvc(pointer_type)
        indexes: tuple[OpConstant] = tuple(
            [
                context.create_on_demand_numerical_constant(
                    OpTypeInt, value=idx, width=32, signed=0
                )
                for idx in indexes
            ]
        )
        return FuzzResult(cls(type=pointer_type, base=base, indexes=indexes))


# class OpArrayLength(OpCode):
#     result_type: Type = None
#     struct: OpTypeStruct = None
#     array_member: int = None
