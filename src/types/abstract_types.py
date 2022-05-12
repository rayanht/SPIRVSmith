from typing import Generic
from typing import TypeVar

from src import Type
from src.patched_dataclass import dataclass


@dataclass
class ScalarType(Type):
    ...


@dataclass
class ContainerType(Type):
    ...


# TODO I fucking hate this type, look into reworking the whole type system
@dataclass
class MiscType(Type):
    ...


T = TypeVar("T", bound=Type)


@dataclass
class UniformContainerType(Generic[T], ContainerType):
    type: T


@dataclass
class MixedContainerType(ContainerType):
    ...
