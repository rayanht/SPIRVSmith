from typing import TYPE_CHECKING

from src import OpCode
from src import ReparametrizationError
from src import Statement
from src import Type
from src import VoidOp
from utils.patched_dataclass import dataclass

if TYPE_CHECKING:
    from src.context import Context


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
