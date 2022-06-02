import random
from dataclasses import field
from typing import NoReturn
from typing import TYPE_CHECKING

from spirv_enums import Capability
from spirv_enums import StorageClass
from typing_extensions import Self

from src import AbortFuzzing
from src import FuzzLeafMixin
from src import FuzzResult
from src import OpCode
from src import ReparametrizationError
from src.patched_dataclass import dataclass

if TYPE_CHECKING:
    from src.context import Context

from src.types.abstract_types import (
    ContainerType,
    MiscType,
    MixedContainerType,
    ScalarType,
    Type,
    UniformContainerType,
)


@dataclass
class EmptyType(MiscType):
    @classmethod
    def fuzz(cls, context: "Context") -> NoReturn:
        MiscType.set_zero_probability(cls, context)
        raise AbortFuzzing


@dataclass
class OpTypeVoid(FuzzLeafMixin, MiscType):
    ...


@dataclass
class OpTypeBool(FuzzLeafMixin, ScalarType):
    def get_base_type(self):
        return self


@dataclass
class OpTypeInt(ScalarType):
    width: int
    signed: int

    @classmethod
    def fuzz(cls, _: "Context") -> FuzzResult[Self]:
        return FuzzResult(cls(width=2**5, signed=int(bool(random.getrandbits(1)))))

    def get_base_type(self):
        return self


@dataclass
class OpTypeFloat(ScalarType):
    width: int

    @classmethod
    def fuzz(cls, _: "Context") -> FuzzResult[Self]:
        return FuzzResult(cls(width=2**5), [])

    def get_base_type(self):
        return self


@dataclass
class OpTypeVector(UniformContainerType[ScalarType]):
    size: int

    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        fuzzed_inner_type: ScalarType = ScalarType.fuzz(context).opcode
        size: int = context.rng.choice([2, 3, 4])
        return FuzzResult(cls(type=fuzzed_inner_type, size=size), [fuzzed_inner_type])

    def __len__(self):
        return self.size

    def get_base_type(self):
        return self.type.get_base_type()


@dataclass
class OpTypeMatrix(UniformContainerType[OpTypeVector]):
    size: int

    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        n_columns: int = context.rng.choice([2, 3, 4])
        n_rows: int = context.rng.choice([2, 3, 4])
        float_type: OpTypeFloat = OpTypeFloat(width=32)
        vector_type: OpTypeVector = OpTypeVector(type=float_type, size=n_rows)
        return FuzzResult(
            cls(type=vector_type, size=n_columns), [float_type, vector_type]
        )

    def __len__(self):
        return self.size

    @staticmethod
    def get_required_capabilities() -> list[Capability]:
        return [Capability.Matrix]

    def get_base_type(self) -> ScalarType:
        return self.type.get_base_type()


# class OpTypeImage(UniformContainerType):
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
#         self.dim = context.rng.choice(list(Dim))
#         self.depth = context.rng.choice([0, 1, 2])
#         self.arrayed = context.rng.choice([0, 1])
#         self.MS = context.rng.choice([0, 1])
#         self.sampled = context.rng.choice([0, 1, 2])
#         self.image_format = context.rng.choice(list(ImageFormat))
#         self.type = ScalarType().fuzz(context)[0]
#         return [self.type, self]


@dataclass
class OpTypeArray(UniformContainerType[ScalarType]):
    length: OpCode

    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        fuzzed_inner_type: ScalarType = ScalarType.fuzz(context).opcode
        length = context.create_on_demand_numerical_constant(
            OpTypeInt, value=context.rng.randint(1, 32), width=32, signed=0
        )
        return FuzzResult(
            cls(type=fuzzed_inner_type, length=length),
            [fuzzed_inner_type],
        )

    def __len__(self):
        return self.length.value

    def get_base_type(self):
        return self.type.get_base_type()


# class OpTypeRuntimeArray(UniformContainerType):

#     def fuzz(self, context: "Context") -> list[OpCode]:
#         self.type = ScalarType().fuzz(context)[0]
#         return [self.type, self]


@dataclass
class OpTypeStruct(MixedContainerType):
    types: tuple[Type, ...]

    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        struct_types = []
        side_effect_types = []
        for _ in range(context.rng.randint(2, 3)):
            # TODO relax parameter type constraint
            fuzzed_parameter_type: FuzzResult = context.rng.choice(
                [OpTypeFloat, OpTypeInt]
            ).fuzz(context)
            struct_types.append(fuzzed_parameter_type.opcode)
            side_effect_types += fuzzed_parameter_type.side_effects
            side_effect_types.append(fuzzed_parameter_type.opcode)
        return FuzzResult(cls(types=tuple(struct_types)), side_effect_types)

    def __len__(self):
        return len(self.types)


@dataclass
class OpTypePointer(MixedContainerType):
    storage_class: StorageClass
    type: Type

    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        fuzzed_type: FuzzResult = context.rng.choice([ScalarType, ContainerType]).fuzz(
            context
        )
        storage_class: StorageClass = context.rng.choice(
            [StorageClass.StorageBuffer, StorageClass.Function]
        )
        return FuzzResult(
            cls(type=fuzzed_type.opcode, storage_class=storage_class),
            fuzzed_type.side_effects + [fuzzed_type.opcode],
        )


@dataclass
class OpTypeFunction(MiscType):
    return_type: Type
    parameter_types: tuple[Type, ...] = field(default_factory=tuple)

    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        if len(context.get_function_types()) >= context.config.limits.n_functions:
            MiscType.set_zero_probability(cls, context)
            raise ReparametrizationError
        # return_type = context.rng.choice([ScalarType, ContainerType])().fuzz(context)
        return_type = OpTypeVoid()
        parameter_types = []
        for _ in range(context.rng.randint(4, 7)):
            parameter_type = context.rng.choice([ScalarType, ContainerType]).fuzz(
                context
            )
            parameter_types.append(parameter_type.opcode)
        return FuzzResult(
            cls(return_type=return_type, parameter_types=tuple(parameter_types)),
            parameter_types,
        )
