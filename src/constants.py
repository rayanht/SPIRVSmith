import random
from typing import TYPE_CHECKING

from src import Constant
from src import OpCode
from src.predicates import HasType
from src.predicates import IsMatrixType

if TYPE_CHECKING:
    from src.context import Context
from src.types.abstract_types import (
    NumericalType,
    Type,
)
from src.types.concrete_types import (
    OpTypeArray,
    OpTypeBool,
    OpTypeInt,
    OpTypeMatrix,
    OpTypeVector,
)
from utils.patched_dataclass import dataclass


class ScalarConstant(Constant):
    ...


class CompositeConstant(Constant):
    ...


class OpConstantTrue(ScalarConstant):
    type: Type = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        self.type = OpTypeBool()
        return [self.type, self]


class OpConstantFalse(ScalarConstant):
    type: Type = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        self.type = OpTypeBool()
        return [self.type, self]


@dataclass
class OpConstant(ScalarConstant):
    type: Type = None
    value: int | float = None

    def fuzz(self, context: "Context") -> list[OpCode]:

        self.type = NumericalType().fuzz(context)[-1]

        if isinstance(self.type, OpTypeInt):
            if self.type.signed:
                self.value = random.SystemRandom().randint(-100, 100)
            else:
                self.value = random.SystemRandom().randint(0, 100)
        else:
            self.value = random.SystemRandom().uniform(0, 100)

        return [self.type, self]


class OpConstantComposite(CompositeConstant):
    type: Type = None
    constituents: tuple[OpCode] = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        composite_type = (
            random.SystemRandom()
            .choice([OpTypeArray, OpTypeVector, OpTypeMatrix])()
            .fuzz(context)
        )
        self.type: OpTypeArray | OpTypeVector | OpTypeMatrix = composite_type[-1]
        self.constituents = []
        if IsMatrixType(self):
            column_type = self.type.type
            for _ in range(len(self.type)):
                column_values = OpConstantComposite()
                column_values.type = column_type
                column_values.constituents = tuple(
                    column_values.fuzz_constituents(context)
                )
                self.constituents.append(column_values)
        else:
            self.constituents = self.fuzz_constituents(context)
            if len(self.constituents) == 0:
                return []
        self.constituents = tuple(self.constituents)
        return [*composite_type, *self.constituents, self]

    def fuzz_constituents(self, context: "Context") -> list[OpCode]:
        base_type: Type = self.type.get_base_type()
        self.constituents = []
        for _ in range(len(self.type)):
            constituent: Constant = context.get_random_operand(HasType(base_type))
            if constituent:
                self.constituents.append(constituent)
            else:
                return []
        return self.constituents
