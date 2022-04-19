import random
from typing import TYPE_CHECKING

from src.operators.memory import MemoryOperator


if TYPE_CHECKING:
    from src.context import Context
from src.enums import StorageClass
from src import (
    OpCode,
)
from src.types.concrete_types import (
    OpTypeBool,
    OpTypePointer,
    OpTypeStruct,
)


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
                        context.symbol_table,
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
                            context.symbol_table,
                        )
                    )
                )
        self.storage_class = storage_class
        if dynamic:
            return [self.type, self]
        return [self]
