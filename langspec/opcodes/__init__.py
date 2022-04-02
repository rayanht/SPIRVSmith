from abc import ABC
from dataclasses import field
import inspect

from typing import TYPE_CHECKING, Dict, Tuple
from uuid import uuid4

if TYPE_CHECKING:
    from langspec.opcodes.context import Context
from patched_dataclass import dataclass
import random
from typing import List
from langspec.enums import Capability

randomization_parameters = {
    "MemoryOperator": "w_memory_operation",
    "LogicalOperator": "w_logical_operation",
    "ArithmeticOperator": "w_arithmetic_operation",
    "ControlFlowOperator": "w_control_flow_operation",
    "FunctionOperator": "w_function_operation",
    "BitwiseOperator": "w_bitwise_operation",
    "ConversionOperator": "w_conversion_operation",
}

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
    "get_base_type",
]


class ReparametrizationError(Exception):
    ...


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
        return hash(tuple([getattr(self, attr) for attr in members(self)]))

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


# A FuzzDelegator is a transient object, we need to commit
# reparametrizations to this global object.
PARAMETRIZATIONS: Dict[str, Dict[str, int]] = {}


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
    def set_zero_probability(cls, target_cls) -> None:
        # There is a tricky case here when an OpCode can be reached
        # from multiple delegators.
        #
        # The delegation path then has a fork in it and when we try
        # to reparametrize it is possible that ot all delegators in
        # the path have been parametrized yet
        PARAMETRIZATIONS[cls.__name__][target_cls.__name__] = 0

    def parametrize(self, context: "Context") -> None:
        subclasses = self.get_subclasses()
        # Get parametrization from config for top-level delegators
        PARAMETRIZATIONS[self.__class__.__name__] = {}
        if "ArithmeticOperator" in map(lambda cls: cls.__name__, subclasses):
            for sub in subclasses:
                PARAMETRIZATIONS[self.__class__.__name__][sub.__name__] = getattr(
                    context.config, randomization_parameters[sub.__name__]
                )
        else:
            for sub in subclasses:
                PARAMETRIZATIONS[self.__class__.__name__][sub.__name__] = 1

    def fuzz(self, context: "Context") -> List[OpCode]:
        if not self.__class__.is_parametrized():
            self.parametrize(context=context)
        subclasses = self.get_subclasses()
        weights = [
            PARAMETRIZATIONS[self.__class__.__name__][sub.__name__]
            for sub in subclasses
        ]
        try:
            return [
                *random.choices(subclasses, weights=weights, k=1)[0]().fuzz(context)
            ]
        except ReparametrizationError:
            return [
                *random.choices(subclasses, weights=weights, k=1)[0]().fuzz(context)
            ]


class FuzzLeaf(OpCode):
    def fuzz(self, context: "Context") -> List[OpCode]:
        return [self]


class Type(FuzzDelegator):
    def get_base_type(self):
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
