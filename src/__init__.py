import hashlib
import pickle
from abc import ABC
from dataclasses import field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.context import Context
from utils.patched_dataclass import dataclass
import random
from src.enums import Capability
from ulid import monotonic as ulid
from ulid import ULID

randomization_parameters = {
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
    "ArithmeticType": "w_arithmetic_type",
    "NumericalType": "w_numerical_type",
    "CompositeConstant": "w_composite_constant",
    "ScalarConstant": "w_scalar_constant",
}

excluded_identifiers = [
    "id",
    "symbol_table",
    # "context",
    "get_required_capabilities",
    "iteritems",
    "keys",
    "resolve_attribute_spasm",
    "to_spasm",
    "fuzz",
    "get_base_type",
]


class ReparametrizationError(Exception):
    ...


def members(inst):
    return tuple(
        [
            x
            for x in inst.__dict__
            # if type(y) != FunctionType
            if x not in excluded_identifiers and not x.startswith("_")
        ]
    )


class VoidOp:
    pass


@dataclass
class OpCode(ABC):
    id: ULID = field(default_factory=ulid.new)

    def __eq__(self, other):
        if type(other) is type(self):
            return [getattr(self, attr) for attr in members(self)] == [
                getattr(other, attr) for attr in members(other)
            ]
        else:
            return False

    def debug_hash(self):
        print(members(self))
        print(tuple([hash(getattr(self, attr)) for attr in members(self)]))
        print("=========")
        return self.__hash__()

    def __hash__(self):
        return int(
            hashlib.sha224(
                pickle.dumps(
                    tuple([hash(getattr(self, attr)) for attr in members(self)])
                )
            ).hexdigest(),
            16,
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({', '.join([str(getattr(self, attr)) for attr in members(self)])})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({', '.join([str(getattr(self, attr)) for attr in members(self)])})"

    @staticmethod
    def get_required_capabilities() -> list[Capability]:
        return []

    @staticmethod
    def fuzz(_: "Context") -> list["OpCode"]:
        return []

    def resolve_attribute_spasm(self, attr, context) -> str:
        if attr.__class__.__name__ == "Context" or attr is None:
            return ""
        elif isinstance(attr, OpCode):
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
            if isinstance(attr, (tuple, list)):
                for _attr in attr:
                    spasm += self.resolve_attribute_spasm(_attr, context)
            else:
                spasm += self.resolve_attribute_spasm(attr, context)
        return spasm


# A FuzzDelegator is a transient object, we need to commit
# reparametrizations to this global object.
PARAMETRIZATIONS: dict[str, dict[str, int]] = {}


class FuzzDelegator(OpCode):
    def get_subclasses(self):
        return self.__class__.__subclasses__()

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
    def set_zero_probability(cls, target_cls) -> None:
        # There is a tricky case here when an OpCode can be reached
        # from multiple delegators.
        #
        # The delegation path then has a fork in it and when we try
        # to reparametrize it is possible that ot all delegators in
        # the path have been parametrized yet
        PARAMETRIZATIONS[cls.__name__][target_cls.__name__] = 0

    def parametrize(self, context: "Context") -> None:
        subclasses_names = set(map(lambda cls: cls.__name__, self.get_subclasses()))
        # Get parametrization from config for top-level delegators
        PARAMETRIZATIONS[self.__class__.__name__] = {}
        for sub in subclasses_names:
            PARAMETRIZATIONS[self.__class__.__name__][sub] = 1
        if any([sub in subclasses_names for sub in randomization_parameters.keys()]):
            for sub in subclasses_names:
                if sub in randomization_parameters:
                    PARAMETRIZATIONS[self.__class__.__name__][sub] = getattr(
                        context.config.strategy, randomization_parameters[sub]
                    )

    def fuzz(self, context: "Context") -> list[OpCode]:
        if not self.__class__.is_parametrized():
            self.parametrize(context=context)
        subclasses = self.get_subclasses()
        weights = [
            PARAMETRIZATIONS[self.__class__.__name__][sub.__name__]
            for sub in subclasses
        ]
        try:
            return [
                *random.SystemRandom()
                .choices(subclasses, weights=weights, k=1)[0]()
                .fuzz(context)
            ]
        except ReparametrizationError:
            return [
                *random.SystemRandom()
                .choices(subclasses, weights=weights, k=1)[0]()
                .fuzz(context)
            ]


class FuzzLeaf(OpCode):
    def fuzz(self, context: "Context") -> list[OpCode]:
        return [self]


class Type(FuzzDelegator):
    @staticmethod
    def get_base_type():
        ...


class Constant(FuzzDelegator):
    type: Type

    def get_base_type(self):
        return self.type.get_base_type()


class Statement(FuzzDelegator):
    def get_base_type(self):
        return self.type.get_base_type()


class Untyped:
    ...


class Signed:
    ...


class Unsigned:
    ...
