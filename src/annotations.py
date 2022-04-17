from dataclasses import dataclass

from src import FuzzLeaf
from src import OpCode
from src import VoidOp
from src.enums import Decoration
from src.types.concrete_types import OpTypeStruct


class Annotation(FuzzLeaf, VoidOp):
    ...


@dataclass
class OpDecorate(Annotation):
    target: OpCode = None
    decoration: Decoration = None
    extra_operands: tuple[int | str, ...] = None


@dataclass
class OpMemberDecorate(Annotation):
    target_struct: OpTypeStruct = None
    member: int = None
    decoration: Decoration = None
    extra_operands: tuple[int | str, ...] = None
