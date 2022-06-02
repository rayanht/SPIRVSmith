import hashlib
import inspect
from abc import ABC
from dataclasses import field
from dataclasses import fields
from enum import Enum
from typing import Generic
from typing import TYPE_CHECKING
from typing import TypeVar

import dill
from typing_extensions import Self

if TYPE_CHECKING:
    from src.context import Context

from spirv_enums import Capability
from ulid import monotonic as ulid

from src.patched_dataclass import dataclass

OpCodeName = str
ParameterName = str

randomization_parameters: dict[OpCodeName, ParameterName] = {
    "MemoryOperator": "w_memory_operation",
    "LogicalOperator": "w_logical_operation",
    "ArithmeticOperator": "w_arithmetic_operation",
    "ControlFlowOperator": "w_control_flow_operation",
    "FunctionOperator": "w_function_operation",
    "BitwiseOperator": "w_bitwise_operation",
    "ConversionOperator": "w_conversion_operation",
    "CompositeOperator": "w_composite_operation",
    "ScalarType": "w_scalar_type",
    "ContainerType": "w_container_type",
    "CompositeConstant": "w_composite_constant",
    "ScalarConstant": "w_scalar_constant",
}


class ReparametrizationError(Exception):
    ...


class AbortFuzzing(Exception):
    ...


@dataclass
class OpCode(ABC):
    id: str = field(default_factory=lambda: ulid.new().str, init=False)

    def members(self) -> tuple[str, ...]:
        return tuple(
            [x.name for x in fields(self.__class__) if x.name not in {"id", "context"}]
        )

    def __eq__(self, other) -> bool:
        return (other.__class__.__name__ == self.__class__.__name__) and (
            hash(self) == hash(other)
        )

    def __hash__(self) -> int:
        return int(
            hashlib.sha224(
                dill.dumps(
                    tuple([hash(getattr(self, attr)) for attr in self.members()])
                )
            ).hexdigest(),
            16,
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({', '.join([str(getattr(self, attr)) for attr in self.members()])})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({', '.join([str(getattr(self, attr)) for attr in self.members()])})"

    @staticmethod
    def get_required_capabilities() -> list[Capability]:
        return []

    @classmethod
    def fuzz(cls, _: "Context") -> "FuzzResult":
        pass

    def resolve_attribute_spasm(self, attr, context: "Context") -> str:
        if (
            attr.__class__.__name__ == "Context"
            or attr is None
            or attr.__class__.__name__ == "EmptyType"
        ):
            return ""
        elif inspect.isclass(attr) and issubclass(attr, OpCode):
            attr_spasm = f" {attr.__name__}"
        elif isinstance(attr, OpCode):
            if isinstance(attr, (Type, Constant)):
                # print("======")
                # print(self, attr)
                attr_spasm = f" %{context.globals[attr]}"
            else:
                attr_spasm = f" %{attr.id}"
        elif isinstance(attr, str) and not isinstance(attr, Enum):
            attr_spasm = f' "{attr}"'
        else:
            attr_spasm = f" {str(attr)}"
        return attr_spasm

    def to_spasm(self, context: "Context") -> str:
        attrs = self.members()
        if self.__class__.__name__ == "OpStore":
            pass
        if isinstance(self, VoidOp):
            spasm = f"{self.__class__.__name__}"
        else:
            spasm = f"%{self.id} = {self.__class__.__name__}"
        for attr_name in attrs:
            attr = getattr(self, attr_name)
            if isinstance(attr, (tuple, list)):
                for _attr in attr:
                    spasm += self.resolve_attribute_spasm(_attr, context)
            else:
                spasm += self.resolve_attribute_spasm(attr, context)
        return spasm


class VoidOp(OpCode):
    ...


T = TypeVar("T", bound=OpCode)


@dataclass
class FuzzResult(Generic[T]):
    opcode: T
    side_effects: list[OpCode] = field(default_factory=list)
    is_opcode_pre_side_effects: bool = field(default_factory=lambda: False)


# A FuzzDelegator is a transient object, we need to commit
# reparametrizations to this global object.
PARAMETRIZATIONS: dict[str, dict[str, int]] = {}


class FuzzDelegator(OpCode):
    @classmethod
    def get_subclasses(cls) -> set["FuzzDelegator"]:
        return set(cls.__subclasses__())

    @classmethod
    def is_parametrized(cls):
        return cls.__name__ in PARAMETRIZATIONS

    @classmethod
    def get_parametrization(cls):
        return PARAMETRIZATIONS[cls.__name__]

    @classmethod
    def reset_parametrizations(cls):
        global PARAMETRIZATIONS
        PARAMETRIZATIONS = {}

    @classmethod
    def set_zero_probability(cls, target_cls, context: "Context") -> None:
        if not cls.is_parametrized():
            cls.parametrize(context=context)
        # There is a tricky case here when an OpCode can be reached
        # from multiple delegators.
        #
        # The delegation path then has a fork in it and when we try
        # to reparametrize it is possible that ot all delegators in
        # the path have been parametrized yet
        PARAMETRIZATIONS[cls.__name__][target_cls.__name__] = 0

    @classmethod
    def parametrize(cls, context: "Context") -> None:
        subclasses_names: set[OpCodeName] = set(
            map(lambda cls: cls.__name__, cls.get_subclasses())
        )
        # Get parametrization from config for top-level delegators
        PARAMETRIZATIONS[cls.__name__] = {}
        for subclass_name in subclasses_names:
            PARAMETRIZATIONS[cls.__name__][subclass_name] = 1
        if any(
            [
                subclass_name in subclasses_names
                for subclass_name in randomization_parameters.keys()
            ]
        ):
            for subclass_name in subclasses_names:
                if subclass_name in randomization_parameters:
                    PARAMETRIZATIONS[cls.__name__][
                        subclass_name
                    ] = context.config.strategy[randomization_parameters[subclass_name]]
        if cls.__name__ == "Statement":
            PARAMETRIZATIONS[cls.__name__]["OpExtInst"] = 0

    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        # TODO this is terrible, there must be a better way
        pass

        if context.config.strategy.enable_ext_glsl_std_450:
            pass
        if not cls.is_parametrized():
            cls.parametrize(context=context)
        subclasses: list["FuzzDelegator"] = list(cls.get_subclasses())
        weights = [PARAMETRIZATIONS[cls.__name__][sub.__name__] for sub in subclasses]
        if sum(weights) == 0 or len(weights) == 0:
            print(cls, subclasses, weights)
        try:
            return context.rng.choices(subclasses, weights=weights, k=1)[0].fuzz(
                context
            )
        except ReparametrizationError:
            return context.rng.choices(subclasses, weights=weights, k=1)[0].fuzz(
                context
            )


@dataclass
class Type(FuzzDelegator):
    @staticmethod
    def get_base_type() -> Self:
        ...


@dataclass
class FuzzLeafMixin:
    @classmethod
    def fuzz(cls, _: "Context") -> FuzzResult[Self]:
        return FuzzResult(cls())


@dataclass
class Constant(FuzzDelegator):
    type: Type

    def get_base_type(self) -> Type:
        return self.type.get_base_type()


@dataclass
class Statement(FuzzDelegator):
    type: Type

    def get_base_type(self) -> Type:
        return self.type.get_base_type()


class Untyped:
    ...


class Signed:
    ...


class Unsigned:
    ...
