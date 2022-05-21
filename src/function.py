import random
from ast import Constant
from typing import Optional
from typing import TYPE_CHECKING

from typing_extensions import Self

from src import AbortFuzzing
from src import FuzzLeafMixin
from src import FuzzResult
from src import OpCode
from src import Untyped
from src import VoidOp
from src.enums import FunctionControlMask
from src.enums import SelectionControlMask
from src.enums import StorageClass
from src.predicates import IsOfType
from src.predicates import IsScalarBoolean

if TYPE_CHECKING:
    from src.context import Context
from src.operators.memory.memory_access import OpVariable, Statement
from src.types.concrete_types import (
    EmptyType,
    OpTypeBool,
    OpTypeFunction,
    OpTypePointer,
    Type,
)
from src.patched_dataclass import dataclass


@dataclass
class FunctionOperator(Statement):
    ...


@dataclass
class OpFunction(OpCode):
    return_type: Type
    function_control_mask: FunctionControlMask
    function_type: OpTypeFunction

    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        op_function: Self = cls(
            context.current_function_type.return_type,
            context.rng.choice(list(FunctionControlMask)),
            context.current_function_type,
        )
        child_context = context.make_child_context(op_function)
        instructions: list[Statement] = fuzz_block(child_context, None)
        return FuzzResult(
            op_function,
            [
                *instructions,
                OpReturn.fuzz(child_context).opcode,
                OpFunctionEnd.fuzz(child_context).opcode,
            ],
        )


@dataclass
class OpFunctionParameter(FuzzLeafMixin):
    type: Type


@dataclass
class OpFunctionEnd(FuzzLeafMixin, VoidOp):
    ...


@dataclass
class OpReturn(FunctionOperator, Untyped, VoidOp):
    # operand: Statement = None

    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        target_type = context.function.function_type.return_type
        # self.operand = None
        return FuzzResult(cls(type=EmptyType()))


@dataclass
class OpFunctionCall(OpCode):
    return_type: Type
    function: OpFunction
    arguments: list[OpCode]


@dataclass
class OpLabel(FuzzLeafMixin, Untyped, OpCode):
    ...


@dataclass
class ControlFlowOperator(Statement):
    ...


@dataclass
class OpSelectionMerge(ControlFlowOperator, Untyped, VoidOp):
    exit_label: OpLabel
    selection_control: SelectionControlMask

    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        if context.get_depth() > context.config.limits.max_depth:
            raise AbortFuzzing
        exit_label = OpLabel.fuzz(context).opcode
        selection_control = SelectionControlMask.NONE
        if_block = fuzz_block(context, exit_label)
        else_block = fuzz_block(context, exit_label)
        true_label = if_block[0]
        false_label = else_block[0]
        try:
            condition = context.rng.choice(
                context.get_statements(
                    lambda s: not isinstance(s, Untyped)
                    and isinstance(s.type, OpTypeBool)
                )
            )
        except IndexError:
            raise AbortFuzzing
        op_branch = OpBranchConditional(
            condition=condition, true_label=true_label, false_label=false_label
        )
        op_selection = cls(
            type=EmptyType(),
            exit_label=exit_label,
            selection_control=selection_control,
        )
        return FuzzResult(
            op_selection, [op_branch, *if_block, *else_block, exit_label], True
        )


@dataclass
class OpLoopMerge(ControlFlowOperator, Untyped, VoidOp):
    merge_label: OpLabel
    continue_label: OpLabel
    selection_control: SelectionControlMask

    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        loop_back_label = OpLabel.fuzz(context).opcode
        pre_loop_branch = OpBranch(loop_back_label)
        loop_back_branch = OpBranch(loop_back_label)
        if context.get_depth() > context.config.limits.max_depth:
            raise AbortFuzzing
        merge_label = OpLabel.fuzz(context).opcode
        selection_control = SelectionControlMask.NONE
        block = fuzz_block(context, None)
        continue_label = block[0]
        condition = context.get_random_operand(IsScalarBoolean)
        loop_entry_branch = OpBranchConditional(
            condition=condition, true_label=continue_label, false_label=merge_label
        )
        op_loop = cls(
            type=EmptyType(),
            merge_label=merge_label,
            continue_label=continue_label,
            selection_control=selection_control,
        )
        return FuzzResult(
            pre_loop_branch,
            [
                loop_back_label,
                op_loop,
                loop_entry_branch,
                *block,
                loop_back_branch,
                merge_label,
            ],
            True,
        )


@dataclass
class OpBranchConditional(FuzzLeafMixin, Untyped, VoidOp):
    condition: Statement
    true_label: OpLabel
    false_label: OpLabel


@dataclass
class OpBranch(FuzzLeafMixin, Untyped, VoidOp):
    label: OpLabel


def fuzz_block(
    context: "Context",
    exit_label: Optional[OpLabel],
) -> tuple[OpCode]:
    block_label: OpLabel = OpLabel.fuzz(context).opcode
    instructions: list[OpCode] = []
    variables: list[OpVariable] = []
    block_context = context.make_child_context()

    while context.rng.random() < block_context.config.strategy.p_statement:
        try:
            fuzzed_opcode: FuzzResult = Statement.fuzz(block_context)
        except AbortFuzzing:
            continue
        nested_block = False
        if isinstance(fuzzed_opcode.opcode, OpSelectionMerge):
            nested_block = True
        if fuzzed_opcode.is_opcode_pre_side_effects:
            instructions.append(fuzzed_opcode.opcode)
        for side_effect in fuzzed_opcode.side_effects:
            match side_effect:
                case Type() | Constant():
                    context.add_to_tvc(side_effect)
                case OpVariable():
                    variables.append(side_effect)
                case _:
                    instructions.append(side_effect)
            continue
        if isinstance(fuzzed_opcode.opcode, Statement) and not nested_block:
            block_context.symbol_table.append(fuzzed_opcode.opcode)
        if (
            not isinstance(fuzzed_opcode.opcode, (OpVariable, OpReturn))
            and not fuzzed_opcode.is_opcode_pre_side_effects
        ):
            instructions.append(fuzzed_opcode.opcode)
        if isinstance(fuzzed_opcode.opcode, OpVariable):
            variables.append(fuzzed_opcode.opcode)
    if exit_label:
        instructions.append(OpBranch(label=exit_label))
    return tuple([block_label, *variables, *instructions])
