from dataclasses import dataclass
import inspect
import random
from typing import TYPE_CHECKING, List, Tuple
from uuid import uuid4

from langspec.enums import (
    AccessQualifier,
    Capability,
    Dim,
    ExecutionModel,
    ImageFormat,
    StorageClass,
)
from langspec.opcodes import (
    FuzzDelegator,
    FuzzLeaf,
    OpCode,
    OpCode,
    ReparametrizationError,
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
    ...


class OpTypeBool(FuzzLeaf, ScalarType):
    def get_base_type(self):
        return self


class OpTypeInt(ScalarType, NumericalType, ArithmeticType):
    width: int = None
    signed: int = None

    def fuzz(self, context: "Context") -> List[OpCode]:
        self.signed = int(bool(random.getrandbits(1)))
        self.width = 2 ** 5  # TODO other widths with capabilities
        return [self]

    def get_base_type(self):
        return self


class OpTypeFloat(ScalarType, NumericalType, ArithmeticType):
    width: int = None

    def fuzz(self, context: "Context") -> List[OpCode]:
        self.width = 2 ** 5  # TODO other widths with capabilities
        return [self]

    def get_base_type(self):
        return self

class OpTypeVector(UniformContainerType, ArithmeticType):
    type: Type = None
    size: int = None

    def fuzz(self, context: "Context") -> List[OpCode]:
        self.size = random.choice([2, 3, 4])  # 8, 16])
        self.type = ScalarType().fuzz(context)[0]
        return [self.type, self]

    def __len__(self):
        return self.size
    
    def get_base_type(self):
        return self.type.get_base_type()


class OpTypeMatrix(UniformContainerType):
    type: Type = None
    size: int = None

    def fuzz(self, context: "Context") -> List[OpCode]:
        self.size = random.choice([2, 3, 4])  # 8, 16])
        matrix_type = OpTypeVector().fuzz(context)
        # This is a hack
        matrix_type[0] = OpTypeFloat().fuzz(context)[0]
        self.type = matrix_type[-1]
        self.type.type = matrix_type[0]
        return [*matrix_type, self]

    def __len__(self):
        return self.size

    def get_required_capabilities(self) -> List[Capability]:
        return [Capability.Matrix]
    
    def get_base_type(self):
        return self.type.get_base_type()


class OpTypeImage(UniformContainerType):
    type: Type = None
    dim: Dim = None
    depth: int = None
    arrayed: int = None
    MS: int = None
    sampled: int = None
    image_format: ImageFormat = None
    # access_qualifier: AccessQualifier = None

    def fuzz(self, context: "Context") -> List[OpCode]:
        # Can't have images in compute shaders
        # Reparameterize probability distribution
        if context.execution_model != ExecutionModel.Fragment:
            UniformContainerType.set_zero_probability(self.__class__)
            # Exception is handled by FuzzDelegator which
            # will randomly pick from the reparametrized 
            # probability distribution
            raise ReparametrizationError
        self.dim = random.choice(list(Dim))
        self.depth = random.choice([0, 1, 2])
        self.arrayed = random.choice([0, 1])
        self.MS = random.choice([0, 1])
        self.sampled = random.choice([0, 1, 2])
        self.image_format = random.choice(list(ImageFormat))
        self.type = ScalarType().fuzz(context)[0]
        return [self.type, self]


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
    
    def get_base_type(self):
        return self.type.get_base_type()


# class OpTypeRuntimeArray(UniformContainerType):
#     type: Type = None

#     def fuzz(self, context: "Context") -> List[OpCode]:
#         self.type = ScalarType().fuzz(context)[0]
#         return [self.type, self]


class OpTypeStruct(MixedContainerType):
    types: Tuple[Type] = None

    def fuzz(self, context: "Context") -> List[OpCode]:
        self.types = []
        side_effect_types = []
        for _ in range(random.randint(2, 5)):
            parameter_type = random.choice([ScalarType, ContainerType])().fuzz(context)
            if parameter_type == []:
                continue
            self.types.append(parameter_type[-1])
            side_effect_types += parameter_type
        self.types = tuple(self.types)
        return [*side_effect_types, *self.types, self]

    def __len__(self):
        return len(self.types)


class OpTypePointer(UniformContainerType):
    storage_class: StorageClass = None
    type: Type = None

    def fuzz(self, context: "Context") -> List[OpCode]:
        # TODO Fragment shaders Output/Input
        self.storage_class = StorageClass.StorageBuffer
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
        for _ in range(random.randint(4, 7)):
            parameter_type = random.choice([ScalarType, ContainerType])().fuzz(context)
            self.parameter_types.append(parameter_type[-1])
            all_types += parameter_type
        self.parameter_types = tuple(self.parameter_types)
        return [*all_types, self]
