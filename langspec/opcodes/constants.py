from copy import deepcopy
import random
from typing import TYPE_CHECKING, List, Tuple, Union

from langspec.opcodes import (
    Constant,
    OpCode,
)

if TYPE_CHECKING:
    from langspec.opcodes.context import Context
from langspec.opcodes.types.abstract_types import (
    ContainerType,
    NumericalType,
    Type,
)
from langspec.opcodes.types.concrete_types import (
    OpTypeArray,
    OpTypeBool,
    OpTypeFloat,
    OpTypeInt,
    OpTypeMatrix,
    OpTypeStruct,
    OpTypeVector,
)
from patched_dataclass import dataclass


class OpConstantTrue(Constant):
    type: Type = None

    def fuzz(self, context: "Context") -> List[OpCode]:
        self.type = OpTypeBool()
        return [self.type, self]


class OpConstantFalse(Constant):
    type: Type = None

    def fuzz(self, context: "Context") -> List[OpCode]:
        self.type = OpTypeBool()
        return [self.type, self]


@dataclass
class OpConstant(Constant):
    type: Type = None
    value: int | float = None

    def fuzz(self, context: "Context") -> List[OpCode]:

        self.type = NumericalType().fuzz(context)[0]

        if isinstance(self.type, OpTypeInt):
            if self.type.signed:
                self.value = random.randint(-100, 100)
            else:
                self.value = random.randint(0, 100)
        else:
            self.value = random.uniform(0, 100)

        return [self.type, self]


class OpConstantComposite(Constant):
    type: Type = None
    constituents: Tuple[OpCode] = None

    def fuzz(self, context: "Context") -> List[OpCode]:
        composite_type = random.choice(
            [OpTypeArray, OpTypeVector] #, OpTypeMatrix]
        )().fuzz(context)
        self.type: OpTypeArray | OpTypeVector = composite_type[-1]
        base_type: Type = self.type.get_base_type()
        self.constituents = []
        if isinstance(base_type, OpTypeBool):
            for _ in range(len(self.type)):
                entry = random.choice([OpConstantTrue, OpConstantFalse])().fuzz(
                    context
                )
                composite_type += entry[:-1]
                self.constituents.append(entry[-1])
        elif isinstance(base_type, OpTypeInt):
            for _ in range(len(self.type)):
                entry = OpConstant().fuzz(context)
                while not isinstance(entry[-1].type, OpTypeInt):
                    entry = OpConstant().fuzz(context)
                new_type = deepcopy(entry[-1].type)
                new_type.width = base_type.width
                new_type.signed = base_type.signed
                if not new_type.signed:
                    entry[-1].value = abs(entry[-1].value)
                entry[-1].type = new_type
                composite_type.append(new_type)
                self.constituents.append(entry[-1])
        elif isinstance(base_type, OpTypeFloat):
            for _ in range(len(self.type)):
                entry = OpConstant().fuzz(context)
                while not isinstance(entry[-1].type, OpTypeFloat):
                    entry = OpConstant().fuzz(context)
                new_type = deepcopy(entry[-1].type)
                new_type.width = base_type.width
                entry[-1].type = new_type
                composite_type.append(new_type)
                self.constituents.append(entry[-1])
        self.constituents = tuple(self.constituents)
        return [*composite_type, *self.constituents, self]
