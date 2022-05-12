from dataclasses import field
from typing import Optional

from src import FuzzLeafMixin
from src import OpCode
from src import VoidOp
from src.enums import Decoration
from src.patched_dataclass import dataclass
from src.types.concrete_types import OpTypeStruct


@dataclass
class Annotation(FuzzLeafMixin, VoidOp):
    ...


@dataclass
class OpDecorate(Annotation):
    target: OpCode
    decoration: Decoration
    extra_operands: Optional[tuple[int | str, ...]] = field(default_factory=tuple)


@dataclass
class OpMemberDecorate(Annotation):
    target_struct: OpTypeStruct
    member: int
    decoration: Decoration
    extra_operands: tuple[int | str, ...] = field(default_factory=tuple)
