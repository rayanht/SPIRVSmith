from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import TypeVar

from src import OpCode
from src.context import Context
from src.operators.arithmetic.scalar_arithmetic import OpSMod
from src.operators.arithmetic.scalar_arithmetic import OpUMod
from src.operators.composite import OpVectorExtractDynamic
from src.operators.composite import OpVectorInsertDynamic

T = TypeVar("T")


class DangerousPattern(ABC, Generic[T]):
    @abstractmethod
    def recondition(self, opcode: T):
        ...

    @abstractmethod
    def get_affected_opcodes(self) -> set[T]:
        ...


OutOfBoundsVectorOperationVulnerableOpCode = (
    OpVectorExtractDynamic | OpVectorInsertDynamic
)


class OutOfBoundsVectorOperation(
    DangerousPattern[OutOfBoundsVectorOperationVulnerableOpCode]
):
    @staticmethod
    def recondition(
        context: Context, opcode: OutOfBoundsVectorOperationVulnerableOpCode
    ):
        operand1 = opcode.index
        index_type = opcode.index.type
        operand2 = context.create_on_demand_numerical_constant(
            index_type.__class__,
            value=len(opcode.vector.type),
            width=index_type.width,
            signed=index_type.signed,
        )

        if index_type.signed:
            mod = OpSMod
        else:
            mod = OpUMod
        op_mod = mod()
        op_mod.type = index_type
        op_mod.operand1 = operand1
        op_mod.operand2 = operand2
        opcode.index = op_mod
        return [op_mod]

    @staticmethod
    def get_affected_opcodes() -> set[OutOfBoundsVectorOperationVulnerableOpCode]:
        return {OpVectorExtractDynamic, OpVectorInsertDynamic}


def recondition(context: Context, spirv_opcodes: list[OpCode]):
    dangerous_patterns = DangerousPattern.__subclasses__()
    i = 0
    j = len(spirv_opcodes)
    reconditioning_side_effects = []
    while i < j:
        opcode = spirv_opcodes[i]
        for dangerous_pattern in dangerous_patterns:
            if opcode.__class__ in dangerous_pattern.get_affected_opcodes():
                reconditioning_side_effects = dangerous_pattern.recondition(
                    context, opcode
                )
                spirv_opcodes = (
                    spirv_opcodes[:i] + reconditioning_side_effects + spirv_opcodes[i:]
                )
                i += len(reconditioning_side_effects)
        i += 1
        j = len(spirv_opcodes)
    return spirv_opcodes
