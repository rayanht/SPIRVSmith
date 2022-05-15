from dataclasses import field

from src import FuzzLeafMixin
from src import OpCode
from src import VoidOp
from src.enums import AddressingModel
from src.enums import Capability
from src.enums import ExecutionMode
from src.enums import ExecutionModel
from src.enums import MemoryModel
from src.function import OpFunction
from src.patched_dataclass import dataclass
from src.types.concrete_types import Type


class OpNop(OpCode):
    ...


@dataclass
class OpUndef(OpCode):
    type: Type


@dataclass
class OpSizeOf(OpCode):
    pointer: Type
    type: Type

    @staticmethod
    def get_required_capabilities() -> list[Capability]:
        return [Capability.Addresses]


@dataclass
class OpEntryPoint(FuzzLeafMixin, VoidOp):
    execution_model: ExecutionModel
    function: OpFunction
    name: str
    interfaces: tuple[OpCode, ...]


@dataclass
class OpMemoryModel(FuzzLeafMixin, VoidOp):
    addressing_model: AddressingModel
    memory_model: MemoryModel

    @staticmethod
    def get_required_capabilities() -> list[Capability]:
        return [Capability.Shader]


@dataclass
class OpExecutionMode(FuzzLeafMixin, VoidOp):
    function: OpFunction
    execution_mode: ExecutionMode
    extra_operands: tuple[int, ...] = field(default_factory=tuple)


@dataclass
class OpCapability(FuzzLeafMixin, VoidOp):
    capability: Capability
