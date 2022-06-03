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


def get_spirvsmith_version() -> str:
    if os.getenv("CI"):
        return "CI"
    repo: git.Repo = git.Repo(os.getcwd())
    tags: list[git.TagReference] = sorted(
        filter(None, repo.tags), key=lambda t: t.commit.committed_datetime
    )
    return tags[-1].name


def find_subclasses(cls: type[OpCode]) -> None:
    for subclass in cls.__subclasses__():
        CLASSES[subclass.__name__] = subclass
        find_subclasses(subclass)


import src.operators.arithmetic.scalar_arithmetic
import src.operators.arithmetic.linear_algebra
import src.operators.bitwise
import src.operators.composite
import src.operators.conversions
import src.operators.logic
import src.operators.memory.memory_access
import src.operators.memory.variable
import src.operators.arithmetic.glsl
import src.annotations
import src.constants
import src.extension
import src.function
import src.misc

CLASSES: dict[str, type[OpCode]] = {}
find_subclasses(OpCode)


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
