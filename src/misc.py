from dataclasses import dataclass
from typing import Sequence

from src import FuzzLeaf
from src import OpCode
from src import VoidOp
from src.enums import AddressingModel
from src.enums import Capability
from src.enums import ExecutionMode
from src.enums import ExecutionModel
from src.enums import MemoryModel
from src.function import OpFunction
from src.types.concrete_types import Type


class OpNop(OpCode):
    pass


class OpUndef(OpCode):
    type: Type = None


class OpSizeOf(OpCode):
    pointer: Type = None
    type: Type = None

    def get_required_capabilities(self) -> list[Capability]:
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

    def get_required_capabilities(self) -> list[Capability]:
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
