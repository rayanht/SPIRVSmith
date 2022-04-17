import random
from typing import TYPE_CHECKING

from src import FuzzLeaf
from src import OpCode
from src import ReparametrizationError
from src.enums import Capability
from src.enums import StorageClass

if TYPE_CHECKING:
    from src.context import Context
from src.types.abstract_types import (
    ArithmeticType,
    ContainerType,
    MiscType,
    MixedContainerType,
    NumericalType,
    ScalarType,
    Type,
    UniformContainerType,
)


class OpTypeVoid(FuzzLeaf, MiscType):
    ...


class OpTypeBool(FuzzLeaf, ScalarType):
    def get_base_type(self):
        return self


class OpTypeInt(ScalarType, NumericalType, ArithmeticType):
    width: int = None
    signed: int = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        self.width = 2**5  # TODO other widths with capabilities
        self.signed = int(bool(random.getrandbits(1)))
        return [self]

    def get_base_type(self):
        return self


class OpTypeFloat(ScalarType, NumericalType, ArithmeticType):
    width: int = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        self.width = 2**5  # TODO other widths with capabilities
        return [self]

    def get_base_type(self):
        return self


class OpTypeVector(UniformContainerType, ArithmeticType):
    type: Type = None
    size: int = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        self.type = ScalarType().fuzz(context)[0]
        self.size = random.SystemRandom().choice([2, 3, 4])
        return [self.type, self]

    def __len__(self):
        return self.size

    def get_base_type(self):
        return self.type.get_base_type()


class OpTypeMatrix(UniformContainerType):
    type: OpTypeVector = None
    size: int = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        matrix_type = OpTypeVector().fuzz(context)[-1]
        matrix_type.type = OpTypeFloat().fuzz(context)[0]
        self.type = matrix_type
        self.size = random.SystemRandom().choice([2, 3, 4])  # 8, 16])
        return [matrix_type.type, matrix_type, self]

    def __len__(self):
        return self.size

    def get_required_capabilities(self) -> list[Capability]:
        return [Capability.Matrix]

    def get_base_type(self):
        return self.type.get_base_type()


# class OpTypeImage(UniformContainerType):
#     type: Type = None
#     dim: Dim = None
#     depth: int = None
#     arrayed: int = None
#     MS: int = None
#     sampled: int = None
#     image_format: ImageFormat = None
#     # access_qualifier: AccessQualifier = None

#     def fuzz(self, context: "Context") -> list[OpCode]:
#         # Can't have images in compute shaders
#         # Reparameterize probability distribution
#         if context.execution_model != ExecutionModel.Fragment:
#             UniformContainerType.set_zero_probability(self.__class__)
#             # Exception is handled by FuzzDelegator which
#             # will randomly pick from the reparametrized
#             # probability distribution
#             raise ReparametrizationError
#         self.dim = random.SystemRandom().choice(list(Dim))
#         self.depth = random.SystemRandom().choice([0, 1, 2])
#         self.arrayed = random.SystemRandom().choice([0, 1])
#         self.MS = random.SystemRandom().choice([0, 1])
#         self.sampled = random.SystemRandom().choice([0, 1, 2])
#         self.image_format = random.SystemRandom().choice(list(ImageFormat))
#         self.type = ScalarType().fuzz(context)[0]
#         return [self.type, self]


class OpTypeArray(UniformContainerType):
    type: Type = None
    length: OpCode = None

    def fuzz(self, context: "Context") -> list[OpCode]:

        self.type = ScalarType().fuzz(context)[0]

        self.length = context.create_on_demand_numerical_constant(
            OpTypeInt, value=random.SystemRandom().randint(1, 32), width=32, signed=0
        )
        return [self.type, self.length.type, self.length, self]

    def __len__(self):
        return self.length.value

    def get_base_type(self):
        return self.type.get_base_type()


# class OpTypeRuntimeArray(UniformContainerType):
#     type: Type = None

#     def fuzz(self, context: "Context") -> list[OpCode]:
#         self.type = ScalarType().fuzz(context)[0]
#         return [self.type, self]


class OpTypeStruct(MixedContainerType):
    types: tuple[Type] = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        self.types = []
        side_effect_types = []
        for _ in range(random.SystemRandom().randint(2, 5)):
            # TODO relax parameter type constraint
            parameter_type = (
                random.SystemRandom().choice([NumericalType])().fuzz(context)
            )
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

    def fuzz(self, context: "Context") -> list[OpCode]:
        self.storage_class = StorageClass.StorageBuffer
        fuzzed_type = (
            random.SystemRandom().choice([ScalarType, ContainerType])().fuzz(context)
        )
        self.type = fuzzed_type[-1]
        return [*fuzzed_type, self]


class OpTypeFunction(MiscType):
    return_type: Type = None
    parameter_types: tuple[Type] = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        if len(context.get_function_types()) >= context.config.limits.n_functions:
            MiscType.set_zero_probability(self.__class__)
            raise ReparametrizationError
        # return_type = random.SystemRandom().choice([ScalarType, ContainerType])().fuzz(context)
        return_type = [OpTypeVoid()]
        self.return_type = return_type[-1]
        self.parameter_types = []
        all_types = return_type
        for _ in range(random.SystemRandom().randint(4, 7)):
            parameter_type = (
                random.SystemRandom()
                .choice([ScalarType, ContainerType])()
                .fuzz(context)
            )
            self.parameter_types.append(parameter_type[-1])
            all_types += parameter_type
        self.parameter_types = tuple(self.parameter_types)
        return [*all_types, self]
