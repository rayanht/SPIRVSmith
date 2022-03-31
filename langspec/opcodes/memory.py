import random
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from langspec.opcodes.context import Context
from langspec.opcodes.types.abstract_types import ScalarType
from patched_dataclass import dataclass
from langspec.enums import StorageClass
from langspec.opcodes import (
    OpCode,
    OpCode,
    Statement,
    Untyped,
    VoidOp,
)
from langspec.opcodes.types.concrete_types import OpTypeBool, OpTypePointer, Type
from langspec.opcodes import OpCode

class MemoryOperator(Statement):
    ...

class OpVariable(MemoryOperator):
    context: "Context" = None
    type: OpTypePointer = None
    storage_class: StorageClass = None

    def fuzz(self, context: "Context") -> List[OpCode]:
        
        if context.function:
            self.storage_class = StorageClass.Function
        else:
            self.storage_class = (
                StorageClass.StorageBuffer if context.is_compute_shader() else StorageClass.Input
            )
        self.context = context
        dynamic = False
        try:
            self.type = random.choice(
                list(
                    filter(
                        lambda t: isinstance(t, OpTypePointer)
                        and t.storage_class == self.storage_class
                        and (
                            self.storage_class == StorageClass.Function
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
            self.type.storage_class = self.storage_class
            target_storage_class = StorageClass.StorageBuffer if context.is_compute_shader() else StorageClass.Input
            if self.storage_class == target_storage_class:
                self.type.type = random.choice(
                    list(
                        filter(
                            lambda tvc: isinstance(tvc, (ScalarType))
                            and not isinstance(tvc, OpTypeBool),
                            context.tvc.keys(),
                        )
                    )
                )
            else:
                self.type.type = random.choice(
                    list(
                        filter(
                            lambda tvc: isinstance(tvc, (ScalarType)),
                            context.symbol_table.keys(),
                        )
                    )
                )
        if dynamic:
            return [self.type, self]
        return [self]


class OpLoad(MemoryOperator):
    type: Type = None
    variable: OpVariable = None
    # memory_operands: Optional[???]

    def validate_opcode(self) -> bool:
        return self.variable.type == self.type

    def fuzz(self, context: "Context") -> List[OpCode]:
        self.variable: OpVariable = random.choice(
            context.get_local_variables() + context.get_global_variables()
        )
        self.type: Type = self.variable.type.type
        return [self]


class OpStore(MemoryOperator, OpCode, Untyped, VoidOp):
    variable: OpVariable = None
    object: OpCode = None
    # memory_operands: Optional[???]

    def fuzz(self, context: "Context") -> List[OpCode]:
        dynamic = False
        try:
            self.object: Statement = random.choice(
                context.get_statements(
                    lambda sym: not isinstance(sym, (OpVariable, Untyped))
                )
            )
        except IndexError:
            return []
        variables: List[OpVariable] = (
            context.get_local_variables() + context.get_global_variables()
        )
        filtered_variables = []
        for variable in variables:
            if variable.type.type == self.object.type:
                filtered_variables.append(variable)
        try:
            variable = random.choice(filtered_variables)
        except IndexError:
            variable = OpVariable()
            variable.storage_class = StorageClass.Function
            variable.type = OpTypePointer()
            variable.type.storage_class = variable.storage_class
            variable.type.type = self.object.type
            variable.context = context
            context.tvc[variable.type] = variable.type.id
            dynamic = True
        self.variable = variable
        if dynamic:
            return [self.variable, self]
        return [self]


# class OpArrayLength(OpCode):
#     result_type: Type = None
#     struct: OpTypeStruct = None
#     array_member: int = None

#     def get_required_capabilities(self) -> List[Capability]:
#         return [Capability.SHADER]
