from src import OpCode
from src import Statement
from src import Type
from src import VoidOp
from utils.patched_dataclass import dataclass


@dataclass
class OpExtension(OpCode, VoidOp):
    name: str = None


@dataclass
class OpExtInstImport(OpCode):
    name: str = None


@dataclass
class OpExtInst(Statement):
    type: Type = None
    extension_set: OpExtInstImport = None
    instruction: OpCode = None
    operands: tuple[Statement] = None
