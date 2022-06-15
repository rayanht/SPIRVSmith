import inspect
from abc import ABC
from dataclasses import field
from dataclasses import fields
from enum import Enum
from typing import Generic
from typing import TYPE_CHECKING
from typing import TypeVar

import numpy as np
from scipy.stats import beta
from typing_extensions import Self

if TYPE_CHECKING:
    from src.context import Context

from spirv_enums import Capability
from ulid import monotonic as ulid

from src.patched_dataclass import dataclass

OpCodeName = str
ParameterName = str

randomization_parameters: dict[OpCodeName, ParameterName] = {
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
        return hash(tuple([getattr(self, attr) for attr in self.members()]))

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
COUNT: int = 0


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
        global COUNT
        COUNT = 0
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
        subclasses_names: list[OpCodeName] = sorted(
            set(map(lambda cls: cls.__name__, cls.get_subclasses()))
        )
        # Get parametrization from config for top-level delegators
        PARAMETRIZATIONS[cls.__name__] = {}
        for subclass_name in subclasses_names:
            PARAMETRIZATIONS[cls.__name__][subclass_name] = 1
        if cls.__name__ == "Statement":
            PARAMETRIZATIONS[cls.__name__]["OpExtInst"] = 0
            subclasses_names.remove("OpExtInst")
            N = len(subclasses_names)
            match context.config.strategy.gp_policy:
                case "uniform":
                    probs = [1 / N] * N
                case "gaussian":
                    mu = context.rng.uniform(0, N)
                    sigma = context.rng.uniform(1.5, 3.5)
                    sample = np.random.normal(loc=mu, scale=sigma, size=100000)
                    sample = np.round(sample).astype(int)
                    sample = [x for x in sample if 0 <= x < N]
                    _, count = np.unique(sample, return_counts=True)
                    probs = count / len(sample)
                case "beta_binomial":
                    mu = context.rng.uniform(0.1, 0.9)
                    sigma = context.rng.uniform(0.1, 0.25)

                    n = (mu * (1 - mu)) / sigma**2
                    a = mu * n
                    b = (1 - mu) * n

                    x = np.linspace(beta.ppf(0.01, a, b), beta.ppf(0.99, a, b), N)
                    pdf = beta.pdf(x, a, b)
                    probs = pdf / pdf.sum()
            for prob, subclass_name in zip(probs, subclasses_names):
                PARAMETRIZATIONS[cls.__name__][subclass_name] = prob

    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        """
        Sentinel
        """
        global COUNT
        if COUNT > context.config.strategy.shader_target_size:
            raise GeneratorExit
        import src.operators.arithmetic.scalar_arithmetic
        import src.operators.arithmetic.linear_algebra
        import src.operators.bitwise
        import src.operators.composite
        import src.operators.conversions
        import src.operators.logic
        import src.operators.memory.memory_access
        import src.operators.memory.variable

        if context.config.strategy.enable_ext_glsl_std_450:
            import src.operators.arithmetic.glsl
        if not cls.is_parametrized():
            cls.parametrize(context=context)
        if context.rng.random() < context.config.strategy.p_mutation:
            Statement.parametrize(context=context)
        subclasses: list[type["FuzzDelegator"]] = list(cls.get_subclasses())
        if cls is Type or issubclass(cls, Type):
            excluded_types = [
                subclass
                for subclass in subclasses
                if subclass.__name__ in context.config.strategy.type_exclusion_set
            ]
            for excluded_type in excluded_types:
                cls.set_zero_probability(excluded_type, context)
        weights = [PARAMETRIZATIONS[cls.__name__][sub.__name__] for sub in subclasses]
        if sum(weights) == 0 or len(weights) == 0:
            print(cls, subclasses, weights)
        try:
            subclass = context.rng.choices(subclasses, weights=weights, k=1)[0]
            fuzzed_subclass = subclass.fuzz(context)
        except ReparametrizationError:
            subclass = context.rng.choices(subclasses, weights=weights, k=1)[0]
            fuzzed_subclass = subclass.fuzz(context)
        if cls.fuzz.__doc__ != subclass.fuzz.__doc__ and not issubclass(
            subclass, (Type, Constant)
        ):
            COUNT += 1
        return fuzzed_subclass


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
