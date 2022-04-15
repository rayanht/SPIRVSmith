from dataclasses import dataclass
from typing import Tuple
from src import FuzzLeaf, OpCode, VoidOp
from src.enums import Decoration
from src.types.concrete_types import OpTypeStruct


class Annotation(FuzzLeaf, VoidOp):
    ...


@dataclass
class OpDecorate(Annotation):
    target: OpCode = None
    decoration: Decoration = None
    extra_operands: Tuple[int | str, ...] = None


@dataclass
class OpMemberDecorate(Annotation):
    target_struct: OpTypeStruct = None
    member: int = None
    decoration: Decoration = None
    extra_operands: Tuple[int | str, ...] = None
