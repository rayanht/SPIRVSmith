import random
from dataclasses import fields
from typing import TYPE_CHECKING

from typing_extensions import Self

from src.operators.memory import MemoryOperator
from src.patched_dataclass import dataclass

if TYPE_CHECKING:
    from src.context import Context
from src.enums import StorageClass
from src import (
    AbortFuzzing,
    FuzzResult,
    OpCode,
    Type,
)
from src.types.concrete_types import (
    OpTypeBool,
    OpTypePointer,
    OpTypeStruct,
)


@dataclass
class OpVariable(MemoryOperator):
    storage_class: StorageClass

    def hashing_members(self):
        return tuple(
            [x.name for x in fields(self.__class__) if x.name not in {"id", "context"}]
        )

    def get_base_type(self) -> Type:
        return self.type.get_base_type()

    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        if context.function:
            storage_class = StorageClass.Function
        else:
            storage_class = (
                StorageClass.StorageBuffer
                if context.is_compute_shader()
                else StorageClass.Input
            )
        try:
            variable_type = random.SystemRandom().choice(
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
            if context.function:
                raise AbortFuzzing
            target_storage_class = (
                StorageClass.StorageBuffer
                if context.is_compute_shader()
                else StorageClass.Input
            )
            if storage_class == target_storage_class:
                pointer_inner_type = random.SystemRandom().choice(
                    list(
                        filter(
                            lambda tvc: isinstance(tvc, (OpTypeStruct))
                            and not isinstance(tvc, OpTypeBool),
                            context.tvc.keys(),
                        )
                    )
                )
            else:
                pointer_inner_type = random.SystemRandom().choice(
                    list(
                        filter(
                            lambda tvc: isinstance(tvc, (OpTypeStruct)),
                            context.symbol_table,
                        )
                    )
                )
            variable_type = OpTypePointer(
                storage_class=storage_class, type=pointer_inner_type
            )
        return FuzzResult(
            cls(type=variable_type, storage_class=storage_class), [variable_type]
        )
