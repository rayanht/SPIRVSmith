import os

import git

from src import OpCode


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
