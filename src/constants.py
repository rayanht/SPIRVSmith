import random
from typing import TYPE_CHECKING

from typing_extensions import Self

from src import AbortFuzzing
from src import Constant
from src import FuzzResult
from src import OpCode
from src.predicates import HasType
from src.predicates import IsMatrixType

if TYPE_CHECKING:
    from src.context import Context
from src.types.abstract_types import (
    Type,
)
from src.types.concrete_types import (
    OpTypeArray,
    OpTypeBool,
    OpTypeFloat,
    OpTypeInt,
    OpTypeMatrix,
    OpTypeVector,
)
from src.patched_dataclass import dataclass


@dataclass
class ScalarConstant(Constant):
    ...


@dataclass
class CompositeConstant(Constant):
    ...


@dataclass
class OpConstantTrue(ScalarConstant):
    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        ScalarConstant.set_zero_probability(cls, context)
        return FuzzResult(cls(type=OpTypeBool()), [OpTypeBool()])


@dataclass
class OpConstantFalse(ScalarConstant):
    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        ScalarConstant.set_zero_probability(cls, context)
        return FuzzResult(cls(type=OpTypeBool()), [OpTypeBool()])


@dataclass
class OpConstant(ScalarConstant):
    value: int | float

    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        fuzzed_type: OpTypeInt | OpTypeFloat = (
            random.SystemRandom().choice([OpTypeInt, OpTypeFloat]).fuzz(context).opcode
        )

        if isinstance(fuzzed_type, OpTypeInt):
            if fuzzed_type.signed:
                return FuzzResult(
                    cls(
                        type=fuzzed_type, value=random.SystemRandom().randint(-100, 100)
                    ),
                    [fuzzed_type],
                )
            return FuzzResult(
                cls(type=fuzzed_type, value=random.SystemRandom().randint(0, 100)),
                [fuzzed_type],
            )
        return FuzzResult(
            cls(type=fuzzed_type, value=random.SystemRandom().uniform(0, 100)),
            [fuzzed_type],
        )


@dataclass
class OpConstantComposite(CompositeConstant):
    constituents: tuple[OpCode, ...]

    @staticmethod
    def fuzz_constituents(base_type: Type, n: int, context: "Context") -> list[OpCode]:
        constituents: list[OpCode] = []
        for _ in range(n):
            constituent: Constant = context.get_random_operand(HasType(base_type))
            if constituent:
                constituents.append(constituent)
            else:
                raise AbortFuzzing
        return constituents

    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        fuzzed_inner_type: FuzzResult[Self] = (
            random.SystemRandom()
            .choice([OpTypeArray, OpTypeVector, OpTypeMatrix])
            .fuzz(context)
        )
        constituents = []
        match fuzzed_inner_type.opcode:
            case OpTypeMatrix():
                column_type: OpTypeVector = fuzzed_inner_type.opcode.type
                for _ in range(len(fuzzed_inner_type.opcode)):
                    column_values = OpConstantComposite(
                        type=column_type,
                        constituents=tuple(
                            cls.fuzz_constituents(
                                column_type.get_base_type(),
                                len(column_type),
                                context,
                            )
                        ),
                    )
                    constituents.append(column_values)
            case OpTypeArray() | OpTypeVector():
                constituents = cls.fuzz_constituents(
                    fuzzed_inner_type.opcode.get_base_type(),
                    len(fuzzed_inner_type.opcode),
                    context,
                )
        return FuzzResult(
            cls(type=fuzzed_inner_type.opcode, constituents=tuple(constituents)),
            [*fuzzed_inner_type.side_effects, fuzzed_inner_type.opcode, *constituents],
        )
