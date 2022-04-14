from copy import deepcopy
import random
from typing import TYPE_CHECKING, List, Tuple, Union
from monitor import Event

from src import (
    Constant,
    OpCode,
)
from src.predicates import HasValidBaseTypeAndSign, HasValidTypeAndSign

if TYPE_CHECKING:
    from src.context import Context
from src.types.abstract_types import (
    ContainerType,
    NumericalType,
    Type,
)
from src.types.concrete_types import (
    OpTypeArray,
    OpTypeBool,
    OpTypeFloat,
    OpTypeInt,
    OpTypeMatrix,
    OpTypeStruct,
    OpTypeVector,
)
from utils.patched_dataclass import dataclass


class ScalarConstant(Constant):
    ...


class CompositeConstant(Constant):
    ...


class OpConstantTrue(ScalarConstant):
    type: Type = None

    def fuzz(self, context: "Context") -> List[OpCode]:
        self.type = OpTypeBool()
        return [self.type, self]


class OpConstantFalse(ScalarConstant):
    type: Type = None

    def fuzz(self, context: "Context") -> List[OpCode]:
        self.type = OpTypeBool()
        return [self.type, self]


@dataclass
class OpConstant(ScalarConstant):
    type: Type = None
    value: int | float = None

    def fuzz(self, context: "Context") -> List[OpCode]:

        self.type = NumericalType().fuzz(context)[-1]

        if isinstance(self.type, OpTypeInt):
            if self.type.signed:
                self.value = random.randint(-100, 100)
            else:
                self.value = random.randint(0, 100)
        else:
            self.value = random.uniform(0, 100)

        return [self.type, self]


class OpConstantComposite(CompositeConstant):
    type: Type = None
    constituents: Tuple[OpCode] = None

    def fuzz(self, context: "Context") -> List[OpCode]:
        composite_type = random.choice(
            [OpTypeArray, OpTypeVector]  # , OpTypeMatrix]
        )().fuzz(context)
        self.type: OpTypeArray | OpTypeVector = composite_type[-1]
        base_type: Type = self.type.get_base_type()
        signedness: bool = None
        if hasattr(base_type, "signed"):
            signedness = base_type.signed
        self.constituents = []
        for _ in range(len(self.type)):
            # context.monitor.info(event=Event.DEBUG, extra={"base_type": base_type})
            constituent: Constant = context.get_random_operand(
                lambda x: HasValidTypeAndSign(x, base_type.__class__, signedness)
            )
            if constituent:
                self.constituents.append(constituent)
            else:
                return []
        self.constituents = tuple(self.constituents)
        return [*composite_type, *self.constituents, self]
