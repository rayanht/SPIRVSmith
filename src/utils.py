import os
import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

import git

if TYPE_CHECKING:
    from run import SPIRVSmithConfig

from src import OpCode


@dataclass
class SubprocessResult:
    exit_code: int
    stdout: str
    stderr: str
    executed_command: str


@dataclass
class ClampedInt:
    value: int
    lower_bound: int
    upper_bound: int

    def increment(self):
        self.value = min(self.value + 1, self.upper_bound)

    def decrement(self):
        self.value = max(self.value - 1, self.lower_bound)

    def get(self):
        return self.value


def get_spirvsmith_version() -> str:
    if os.getenv("CI"):
        return "CI"
    repo: git.Repo = git.Repo(os.getcwd())
    tags: list[git.TagReference] = sorted(
        filter(None, repo.tags), key=lambda t: t.commit.committed_datetime
    )
    return tags[-1].name


def get_opcode_class_from_name(opcode_name: str) -> OpCode:
    import src.operators.arithmetic.scalar_arithmetic
    import src.operators.arithmetic.linear_algebra
    import src.operators.arithmetic.glsl
    import src.operators.memory.memory_access
    import src.operators.memory.variable
    import src.operators.bitwise
    import src.operators.composite
    import src.operators.conversions
    import src.operators.logic
    import src.annotations
    import src.constants
    import src.extension
    import src.function

    subclasses: set[OpCode] = set()
    find_subclasses_dfs(subclasses, OpCode)
    opcode_lookup: dict[str, OpCode] = dict(
        zip(map(lambda cls: cls.__name__, subclasses), subclasses)
    )
    return opcode_lookup[opcode_name]


def find_subclasses_dfs(subclasses: set[OpCode], cls: OpCode) -> None:
    for subclass in cls.__subclasses__():
        subclasses.add(subclass)
        find_subclasses_dfs(subclasses, subclass)


def mutate_config(config: "SPIRVSmithConfig") -> None:
    mutable_fields: list[str] = [
        field
        for field in config.strategy.keys()
        if field
        not in {
            "mutations_config",
            "mutation_rate",
            "enable_ext_glsl_std_450",
            "p_statement",
            "optimiser_fuzzing_iterations",
        }
    ]
    mutation_target: str = random.SystemRandom().choice(mutable_fields)
    config.strategy[mutation_target] = random.SystemRandom().randint(
        *config.strategy.mutations_config[mutation_target]
    )
