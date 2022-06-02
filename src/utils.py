import os
import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

import git

if TYPE_CHECKING:
    from run import SPIRVSmithConfig

from src import OpCode

# Lowest common denominator to allow testing with MoltenVK
TARGET_VULKAN_VERSION = "1.1"
TARGET_SPIRV_VERSION = "spv1.3"


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
    pass

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
            "p_picking_statement_operand",
        }
    ]
    mutation_target: str = random.SystemRandom().choice(mutable_fields)
    config.strategy[mutation_target] = random.SystemRandom().randint(
        *config.strategy.mutations_config[mutation_target].values()
    )
