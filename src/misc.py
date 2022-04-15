from src.function import OpFunction
from dataclasses import dataclass
from src import (
    FuzzLeaf,
    OpCode,
    VoidOp,
)
from uuid import uuid4
from typing import List, Sequence
from src.enums import (
    AddressingModel,
    Capability,
    ExecutionMode,
    ExecutionModel,
    MemoryModel,
)
from src.types.concrete_types import Type


class OpNop(OpCode):
    pass


class OpUndef(OpCode):
    type: Type = None


class OpSizeOf(OpCode):
    pointer: Type = None
    type: Type = None

    def get_required_capabilities(self) -> List[Capability]:
        return [Capability.Addresses]


class OpEntryPoint(FuzzLeaf, VoidOp):
    execution_model: ExecutionModel = None
    function: OpFunction = None
    name: str = None
    interfaces: Sequence[OpCode] = None

    def __init__(
        self,
        execution_model: ExecutionModel,
        function: OpFunction,
        name: str,
        interfaces: Sequence[OpCode],
    ) -> None:
        self.execution_model = execution_model
        self.function = function
        self.name = name
        self.interfaces = interfaces
        super().__init__()


class OpMemoryModel(FuzzLeaf, VoidOp):
    addressing_model: AddressingModel = None
    memory_model: MemoryModel = None

    def __init__(
        self, addressing_model: AddressingModel, memory_model: MemoryModel
    ) -> None:
        self.addressing_model = addressing_model
        self.memory_model = memory_model
        super().__init__()

    def get_required_capabilities(self) -> List[Capability]:
        return [Capability.Shader]


@dataclass
class OpExecutionMode(FuzzLeaf, VoidOp):
    function: OpFunction = None
    execution_mode: ExecutionMode = None

    def __init__(self, function: OpFunction, execution_mode: ExecutionMode) -> None:
        self.function = function
        self.execution_mode = execution_mode
        super().__init__()


@dataclass
class OpCapability(FuzzLeaf, VoidOp):
    capability: Capability = None

    def __init__(self, capability: Capability) -> None:
        self.capability = capability
        super().__init__()
