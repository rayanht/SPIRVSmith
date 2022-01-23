import random
from typing import TYPE_CHECKING, List, Tuple
from uuid import uuid4

from langspec.enums import StorageClass
from langspec.opcodes import (
    FuzzLeaf,
    OpCode,
    OpCode,
)

if TYPE_CHECKING:
    from langspec.opcodes.context import Context
from langspec.opcodes.types.abstract_types import (
    ArithmeticType,
    ContainerType,
    MixedContainerType,
    NumericalType,
    ScalarType,
    Type,
    UniformContainerType,
)


class OpTypeVoid(FuzzLeaf, Type):
    pass


class OpTypeInt(ScalarType, NumericalType, ArithmeticType):
    width: int = None
    signed: int = None

    def fuzz(self, context: "Context") -> List[OpCode]:
        self.signed = int(bool(random.getrandbits(1)))
        self.width = 2 ** 5  # TODO other widths with capabilities
        return [self]


class OpTypeFloat(ScalarType, NumericalType, ArithmeticType):
    width: int = None

    def fuzz(self, context: "Context") -> List[OpCode]:
        self.width = 2 ** 5  # TODO other widths with capabilities
        return [self]


class OpTypeBool(FuzzLeaf, ScalarType):
    pass


class OpTypeVector(UniformContainerType, ArithmeticType):
    type: Type = None
    size: int = None

    def fuzz(self, context: "Context") -> List[OpCode]:
        self.size = random.choice([2, 3, 4])  # 8, 16])
        self.type = ScalarType().fuzz(context)[0]
        return [self.type, self]

    def __len__(self):
        return self.size


class OpTypePointer(UniformContainerType):
    storage_class: StorageClass = None
    type: Type = None

    def fuzz(self, context: "Context") -> List[OpCode]:
        self.storage_class = random.choice(list(StorageClass))
        fuzzed_type = random.choice([ScalarType, ContainerType])().fuzz(context)
        self.type = fuzzed_type[-1]
        if self.type is None:
            print("??????")
        return [*fuzzed_type, self]


class OpTypeFunction(Type):
    return_type: Type = None
    parameter_types: Tuple[Type] = None

    def fuzz(self, context: "Context") -> List[OpCode]:

        # return_type = random.choice([ScalarType, ContainerType])().fuzz(context)
        return_type = [OpTypeVoid()]
        self.return_type = return_type[-1]
        self.parameter_types = []
        all_types = return_type
        for _ in range(random.randint(0, 5)):
            parameter_type = random.choice([ScalarType, ContainerType])().fuzz(context)
            self.parameter_types.append(parameter_type[-1])
            all_types += parameter_type
        self.parameter_types = tuple(self.parameter_types)
        return [*all_types, self]


class OpTypeArray(UniformContainerType):
    type: Type = None
    length: OpCode = None

    def fuzz(self, context: "Context") -> List[OpCode]:

        self.type = ScalarType().fuzz(context)[0]
        from langspec.opcodes.constants import OpConstant

        self.length = OpConstant()
        self.length.type = OpTypeInt()
        self.length.type.signed = 0
        self.length.type.width = 32
        self.length.value = random.randint(1, 32)
        return [self.type, self.length.type, self.length, self]

    def __len__(self):
        return self.length.value


class OpTypeStruct(MixedContainerType):
    types: Tuple[Type] = None

    def fuzz(self, context: "Context") -> List[OpCode]:
        self.types = []
        side_effect_types = []
        for _ in range(random.randint(0, 5)):
            parameter_type = random.choice([ScalarType, ContainerType])().fuzz(context)
            self.types.append(parameter_type[-1])
            side_effect_types += parameter_type
        self.types = tuple(self.types)
        return [*side_effect_types, *self.types, self]

    def __len__(self):
        return len(self.types)


class OpTypeRuntimeArray(UniformContainerType):
    type: Type = None

    def fuzz(self, context: "Context") -> List[OpCode]:
        self.type = ScalarType().fuzz(context)[0]
        return [self.type, self]
