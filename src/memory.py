import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.context import Context
from src.enums import StorageClass
from src import (
    OpCode,
    Statement,
    Untyped,
    VoidOp,
)
from src.types.concrete_types import OpTypeBool, OpTypePointer, OpTypeStruct, Type


class MemoryOperator(Statement):
    ...


class OpVariable(MemoryOperator):
    context: "Context" = None
    type: OpTypePointer = None
    storage_class: StorageClass = None

    def fuzz(self, context: "Context") -> list[OpCode]:

        if context.function:
            storage_class = StorageClass.Function
        else:
            storage_class = (
                StorageClass.StorageBuffer
                if context.is_compute_shader()
                else StorageClass.Input
            )
        self.context = context
        dynamic = False
        try:
            self.type = random.SystemRandom().choice(
                list(
                    filter(
                        lambda t: isinstance(t, OpTypePointer)
                        and t.storage_class == storage_class
                        and (
                            storage_class == StorageClass.Function
                            if isinstance(t, OpTypeBool)
                            else False
                        )
                        # No doubly pointers in Logical Addressing
                        and not isinstance(t.type, OpTypePointer),
                        context.symbol_table.keys(),
                    )
                )
            )
        except IndexError:
            dynamic = True
            if context.function:
                return []
            self.type = OpTypePointer()
            self.type.storage_class = storage_class
            target_storage_class = (
                StorageClass.StorageBuffer
                if context.is_compute_shader()
                else StorageClass.Input
            )
            if storage_class == target_storage_class:
                self.type.type = random.SystemRandom().choice(
                    list(
                        filter(
                            lambda tvc: isinstance(tvc, (OpTypeStruct))
                            and not isinstance(tvc, OpTypeBool),
                            context.tvc.keys(),
                        )
                    )
                )
            else:
                self.type.type = random.SystemRandom().choice(
                    list(
                        filter(
                            lambda tvc: isinstance(tvc, (OpTypeStruct)),
                            context.symbol_table.keys(),
                        )
                    )
                )
        self.storage_class = storage_class
        if dynamic:
            return [self.type, self]
        return [self]


class OpLoad(MemoryOperator):
    type: Type = None
    variable: OpVariable = None
    # memory_operands: Optional[???]

    def fuzz(self, context: "Context") -> list[OpCode]:
        variable: OpVariable = random.SystemRandom().choice(
            list(
                filter(
                    lambda x: x.storage_class != StorageClass.Output,
                    context.get_local_variables() + context.get_global_variables(),
                )
            )
        )
        self.type: Type = variable.type.type
        self.variable = variable
        return [self]


class OpStore(MemoryOperator, OpCode, Untyped, VoidOp):
    variable: OpVariable = None
    object: OpCode = None
    # memory_operands: Optional[???]

    def fuzz(self, context: "Context") -> list[OpCode]:
        dynamic = False
        try:
            object: Statement = random.SystemRandom().choice(
                context.get_statements(
                    lambda sym: not isinstance(sym, (OpVariable, Untyped))
                )
            )
        except IndexError:
            return []
        variables: list[OpVariable] = (
            context.get_local_variables() + context.get_global_variables()
        )
        filtered_variables = []
        for variable in variables:
            if (
                variable.type.type == object.type
                and variable.storage_class != StorageClass.Input
            ):
                filtered_variables.append(variable)
        try:
            variable = random.SystemRandom().choice(filtered_variables)
        except IndexError:
            variable = context.create_on_demand_variable(
                StorageClass.Function, object.type
            )
            dynamic = True
        self.variable = variable
        self.object = object
        if dynamic:
            return [self.variable, self]
        return [self]


# class OpAccessChain(MemoryOperator):
#     type: Type = None
#     base: OpCode = None
#     indexes: list[OpCode] = []

#     def fuzz(self, context: "Context") -> list[OpCode]:
#         self.base: OpVariable = random.SystemRandom().choice(
#             context.get_local_variables() + context.get_global_variables()
#         )
#         self.type: Type = self.base.type.type
#         return [self]

# class OpArrayLength(OpCode):
#     result_type: Type = None
#     struct: OpTypeStruct = None
#     array_member: int = None

#     def get_required_capabilities(self) -> list[Capability]:
#         return [Capability.SHADER]
