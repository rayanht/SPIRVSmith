from abc import ABC
from dataclasses import field

from typing import TYPE_CHECKING, Protocol, Tuple
from uuid import uuid4

if TYPE_CHECKING:
    from langspec.opcodes.context import Context
from patched_dataclass import dataclass
import random
from typing import List
from langspec.enums import Capability


class _Intersection:
    def __getitem__(self, bases):
        full_bases = bases + (Protocol,)

        class Inter(*full_bases):
            ...

        return Inter


Intersection = _Intersection()

excluded_identifiers = [
    "id",
    "symbol_table",
    "context",
    "get_required_capabilities",
    "iteritems",
    "keys",
    "resolve_attribute_spasm",
    "to_spasm",
    "validate_opcode",
    "fuzz",
]


def members(inst):
    return tuple(
        [
            x
            for x in inst.__class__.__dict__
            # if type(y) != FunctionType
            if x not in excluded_identifiers and not x.startswith("_")
        ]
    )


class VoidOp:
    pass


@dataclass
class OpCode(ABC):
    id: str = field(default_factory=uuid4)

    def __eq__(self, other):
        if type(other) is type(self):
            return [getattr(self, attr) for attr in members(self)] == [
                getattr(other, attr) for attr in members(other)
            ]
        else:
            return False

    def __hash__(self):
        # print(
        #     self.__class__.__name__,
        #     self.__members(),
        #     tuple([getattr(self, attr) for attr in self.__members()]),
        # )
        return hash(tuple([getattr(self, attr) for attr in members(self)]))

    def validate_opcode(self) -> bool:
        return True

    def get_required_capabilities(self) -> List[Capability]:
        return []

    def fuzz(self, context: "Context") -> List["OpCode"]:
        return []

    def resolve_attribute_spasm(self, attr, context) -> str:
        if isinstance(attr, OpCode):
            if isinstance(attr, (Type, Constant)):
                attr_spasm = f" %{context.tvc[attr]}"
            else:
                attr_spasm = f" %{attr.id}"
        elif isinstance(attr, str):
            attr_spasm = f' "{attr}"'
        else:
            attr_spasm = f" {str(attr)}"
        return attr_spasm

    def to_spasm(self, context: "Context") -> str:
        attrs = members(self)
        if isinstance(self, VoidOp):
            spasm = f"{self.__class__.__name__}"
        else:
            spasm = f"%{self.id} = {self.__class__.__name__}"
        for attr_name in attrs:
            attr = getattr(self, attr_name)
            if isinstance(attr, (Tuple, List)):
                for _attr in attr:
                    spasm += self.resolve_attribute_spasm(_attr, context)
            else:
                spasm += self.resolve_attribute_spasm(attr, context)
        return spasm


class FuzzDelegator(OpCode):
    def fuzz(self, context: "Context") -> List[OpCode]:
        return [*random.choice(self.__class__.__subclasses__())().fuzz(context)]


class FuzzLeaf(OpCode):
    def fuzz(self, context: "Context") -> List[OpCode]:
        return [self]


class Type(FuzzDelegator):
    pass


class Constant(FuzzDelegator):
    type: Type


class Statement(FuzzDelegator):
    pass


class Untyped:
    pass
