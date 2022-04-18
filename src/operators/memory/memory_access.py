import random
from typing import TYPE_CHECKING

from src.constants import OpConstant
from src.operators.memory import MemoryOperator
from src.operators.memory.variable import OpVariable
from src.predicates import And
from src.predicates import HasType
from src.predicates import IsCompositeType
from src.predicates import IsInputVariable
from src.predicates import IsMatrixType
from src.predicates import IsOutputVariable
from src.predicates import IsPointerType
from src.predicates import IsStructType
from src.predicates import IsVariable
from src.predicates import Not

if TYPE_CHECKING:
    from src.context import Context
from src.enums import StorageClass
from src import (
    OpCode,
    Statement,
    Untyped,
    VoidOp,
)
from src.types.concrete_types import (
    OpTypeBool,
    OpTypeInt,
    OpTypePointer,
    OpTypeStruct,
    Type,
)


class OpLoad(MemoryOperator):
    type: Type = None
    variable: OpVariable = None
    # memory_operands: Optional[???]

    def fuzz(self, context: "Context") -> list[OpCode]:
        variable: OpVariable = random.SystemRandom().choice(
            list(
                filter(
                    Not(IsOutputVariable),
                    context.get_local_variables() + context.get_global_variables(),
                )
            )
        )
        self.type: Type = variable.type.type
        self.variable = variable
        return [self]


class OpStore(MemoryOperator, OpCode, Untyped, VoidOp):
    pointer: OpTypePointer = None
    object: OpCode = None
    # memory_operands: Optional[???]

    def fuzz(self, context: "Context") -> list[OpCode]:
        pointer: OpTypePointer = context.get_random_operand(IsPointerType)
        if not pointer:
            return []
        target_object: Statement = context.get_random_operand(
            HasType(pointer.type.type)
        )
        if not object:
            return []
        self.pointer = pointer
        self.object = target_object
        return [self]


class OpAccessChain(MemoryOperator):
    type: Type = None
    base: OpVariable = None
    indexes: tuple[OpConstant] = []

    def fuzz(self, context: "Context") -> list[OpCode]:
        predicate = lambda var: IsCompositeType(var.type)
        base: OpVariable = random.SystemRandom().choice(
            list(filter(predicate, context.get_storage_buffers()))
        )
        if base is None:
            return []
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
        self.type = OpTypePointer()
        self.type.storage_class = base.storage_class
        self.type.type = pointer_inner_type
        context.add_to_tvc(self.type)
        self.base = base
        self.indexes: tuple[OpConstant] = tuple(
            [
                context.create_on_demand_numerical_constant(
                    OpTypeInt, value=idx, width=32, signed=0
                )
                for idx in indexes
            ]
        )
        return [self]


# class OpArrayLength(OpCode):
#     result_type: Type = None
#     struct: OpTypeStruct = None
#     array_member: int = None
