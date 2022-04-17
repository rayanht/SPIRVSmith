import random
from typing import Optional
from typing import TYPE_CHECKING

from src import FuzzLeaf
from src import OpCode
from src import Untyped
from src import VoidOp
from src.enums import FunctionControlMask
from src.enums import SelectionControlMask

if TYPE_CHECKING:
    from src.context import Context
from src.memory import OpVariable, Statement
from src.types.concrete_types import OpTypeBool, OpTypeFunction, Type
from utils.patched_dataclass import dataclass


class FunctionOperator(Statement):
    ...


class OpFunction(OpCode):
    context: "Context" = None
    return_type: Type = None
    function_control_mask: FunctionControlMask = None
    function_type: OpTypeFunction = None

    def __init__(
        self,
        return_type: Type = None,
        function_type: OpTypeFunction = None,
    ) -> None:
        self.return_type: Type = return_type
        self.function_control_mask: FunctionControlMask = random.SystemRandom().choice(
            list(FunctionControlMask)
        )
        self.function_type: OpTypeFunction = function_type
        super().__init__()

    def fuzz(self, context: "Context") -> list[OpCode]:
        self.context = context.make_child_context(self)
        instructions: list[Statement] = fuzz_block(self.context, None)
        return [
            self,
            *instructions,
            *OpReturn().fuzz(self.context),
            *OpFunctionEnd().fuzz(self.context),
        ]


@dataclass
class OpFunctionParameter(FuzzLeaf):
    type: Type = None


class OpFunctionEnd(FuzzLeaf, VoidOp):
    pass


class OpReturn(FunctionOperator, OpCode, Untyped, VoidOp):
    # operand: Statement = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        target_type = context.function.function_type.return_type
        # self.operand = None
        return [self]


class OpFunctionCall(OpCode):
    return_type: Type = None
    function: OpFunction = None
    arguments: list[OpCode] = None


class OpLabel(FuzzLeaf, Untyped):
    pass


class ControlFlowOperator(Statement):
    ...


class OpSelectionMerge(ControlFlowOperator, Untyped, VoidOp):
    exit_label: OpLabel = None
    selection_control: SelectionControlMask = None

    def fuzz(self, context: "Context") -> list[OpCode]:
        if context.get_depth() > context.config.limits.max_depth:
            return []
        self.exit_label = OpLabel().fuzz(context)[0]
        self.selection_control = None  # TODO
        if_block = fuzz_block(context, self.exit_label)
        else_block = fuzz_block(context, self.exit_label)
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
            return []
        op_branch = OpBranchConditional(
            condition=condition, true_label=true_label, false_label=false_label
        )
        return [self, op_branch, *if_block, *else_block, self.exit_label]


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
class OpBranchConditional(FuzzLeaf, Untyped, VoidOp):
    condition: Statement = None
    true_label: OpLabel = None
    false_label: OpLabel = None


@dataclass
class OpBranch(FuzzLeaf, Untyped, VoidOp):
    label: OpLabel = None


def fuzz_block(context: "Context", exit_label: Optional[OpLabel]) -> tuple[OpCode]:
    block_label: OpLabel = OpLabel().fuzz(context)[0]
    instructions: list[OpCode] = []
    variables: list[OpVariable] = []
    block_context = context.make_child_context()
    # TODO this is terrible, there must be a better way
    import src.operators.arithmetic.scalar_arithmetic
    import src.operators.arithmetic.linear_algebra
    import src.operators.logic
    import src.operators.bitwise
    import src.operators.conversions
    import src.operators.composite

    while random.SystemRandom().random() < context.config.strategy.p_statement:
        opcodes: list[OpCode] = Statement().fuzz(block_context)
        nested_block = False
        for statement in opcodes:
            if isinstance(statement, OpSelectionMerge):
                nested_block = True
                break
            if isinstance(statement, Statement) and not nested_block:
                block_context.symbol_table[statement] = statement.id
            if not isinstance(statement, (OpVariable, OpReturn)):
                instructions.append(statement)
            if isinstance(statement, OpVariable):
                variables.append(statement)
        if nested_block:
            nested_block_variables = filter(
                lambda s: isinstance(s, OpVariable), opcodes
            )
            nested_block_instructions = filter(
                lambda s: not isinstance(s, OpVariable), opcodes
            )
            variables += nested_block_variables
            instructions += nested_block_instructions
    if exit_label:
        instructions.append(OpBranch(label=exit_label))
    return tuple([block_label, *variables, *instructions])
