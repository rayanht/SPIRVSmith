from src import OpCode
from src import Statement
from src import VoidOp
from src.patched_dataclass import dataclass


@dataclass
class OpExtension(VoidOp):
    name: str


@dataclass
class OpExtInstImport(OpCode):
    name: str


@dataclass
class OpExtInst(Statement):
    extension_set: OpExtInstImport
    instruction: OpCode
    operands: tuple[OpCode, ...]
