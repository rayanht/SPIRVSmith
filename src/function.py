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

if TYPE_CHECKING:
    from src.context import Context
from src.operators.memory.memory_access import OpVariable, Statement
from src.types.concrete_types import (
    EmptyType,
    OpTypeBool,
    OpTypeFunction,
    OpTypeVoid,
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
            random.SystemRandom().choice(list(FunctionControlMask)),
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
            condition = random.SystemRandom().choice(
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


# class OpLoopMerge(ControlFlowOperator, Untyped, VoidOp):
#     merge_label: OpLabel = None
#     continue_label: OpLabel = None
#     selection_control: SelectionControlMask = None

#     def fuzz(self, context: "Context") -> list[OpCode]:
#         if context.get_depth() > context.config.limits.max_depth:
#             return []
#         self.merge_label = OpLabel().fuzz(context)[0]
#         self.selection_control = None  # TODO
#         loop_label = OpLabel().fuzz(context)[0]
#         block = fuzz_block(context, loop_label)
#         try:
#             condition = random.SystemRandom().choice(context.get_statements(
#                 lambda s: not isinstance(s, Untyped) and isinstance(s.type, OpTypeBool)
#             ))
#         except IndexError:
#             return []
#         op_branch = OpBranchConditional(
#             condition=condition, true_label=self.continue_label, false_label=self.merge_label
#         )
#         return [loop_label, self, op_branch, *block, self.merge_label]


# class OpSwitch(ControlFlowOperator, Untyped, VoidOp):
#     selection_control: SelectionControlMask = None
#     default_label: OpLabel = None
#     case_labels: list[OpLabel] = None
#     value: OpCode = None

#     def fuzz(self, context: "Context") -> tuple[OpCode]:
#         if context.get_depth() > context.limits.max_depth:
#             return []
#         self.selection_control = random.SystemRandom().choice(list(SelectionControlMask))
#         self.default_label = OpLabel().fuzz(context)[0]
#         self.case_labels = []
#         for _ in range(random.SystemRandom().randint(1, 5)):
#             self.case_labels.append(OpLabel().fuzz(context)[0])
#         self.value = random.SystemRandom().choice(context.get_statements(
#                 lambda s: not isinstance(s, Untyped) and isinstance(s.type, OpTypeBool)
#             )
#         ).fuzz(context)[0]
#         return [self, *self.case_labels, self.default_label, self.value]


@dataclass
class OpBranchConditional(FuzzLeafMixin, Untyped, VoidOp):
    condition: Statement
    true_label: OpLabel
    false_label: OpLabel


@dataclass
class OpBranch(FuzzLeafMixin, Untyped, VoidOp):
    label: OpLabel


def fuzz_block(context: "Context", exit_label: Optional[OpLabel]) -> tuple[OpCode]:
    block_label: OpLabel = OpLabel.fuzz(context).opcode
    instructions: list[OpCode] = []
    variables: list[OpVariable] = []
    block_context = context.make_child_context()
    # TODO this is terrible, there must be a better way
    # import src.operators.arithmetic.scalar_arithmetic
    # import src.operators.arithmetic.linear_algebra
    # import src.operators.logic
    # import src.operators.bitwise
    # import src.operators.conversions
    # import src.operators.composite

    # if context.config.strategy.enable_ext_glsl_std_450:
    #     import src.operators.arithmetic.glsl

    while random.SystemRandom().random() < context.config.strategy.p_statement:
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
