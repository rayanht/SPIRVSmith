import random
from typing import TYPE_CHECKING, List, Optional, Tuple
from uuid import UUID, uuid4

from langspec.enums import FunctionControlMask, SelectionControlMask
from langspec.opcodes.constants import OpConstantTrue
from langspec.opcodes import (
    FuzzLeaf,
    OpCode,
    OpCode,
    Untyped,
    VoidOp,
)

if TYPE_CHECKING:
    from langspec.opcodes.context import Context
from langspec.opcodes.memory import OpLoad, OpVariable, Statement
from langspec.opcodes.types.concrete_types import OpTypeBool, OpTypeFunction, Type
from patched_dataclass import dataclass


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
        self.function_type: OpTypeFunction = function_type
        super().__init__()

    def validate_opcode(self) -> bool:
        return self.function_type.return_type == self.return_type

    def fuzz(self, context: "Context") -> List[OpCode]:
        self.context = context.make_child_context(self)
        self.function_control_mask = random.choice(list(FunctionControlMask))
        parameters: List[OpFunctionParameter] = []
        for parameter_type in self.function_type.parameter_types:
            parameters += OpFunctionParameter(type=parameter_type).fuzz(self.context)
        instructions: List[Statement] = fuzz_block(self.context, None)
        return [
            self,
            *parameters,
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

    def fuzz(self, context: "Context") -> List[OpCode]:
        target_type = context.function.function_type.return_type
        # self.operand = None
        return [self]


class OpFunctionCall(OpCode):
    return_type: Type = None
    function: OpFunction = None
    arguments: List[OpCode] = None


class OpLabel(FuzzLeaf, Untyped):
    pass


class ControlFlowOperator(Statement):
    ...

class OpSelectionMerge(ControlFlowOperator, Untyped, VoidOp):
    exit_label: OpLabel = None
    selection_control: SelectionControlMask = None

    def fuzz(self, context: "Context") -> List[OpCode]:
        if context.get_depth() > context.config.max_depth:
            return []
        self.exit_label = OpLabel().fuzz(context)[0]
        self.selection_control = None  # TODO
        if_block = fuzz_block(context, self.exit_label)
        else_block = fuzz_block(context, self.exit_label)
        true_label = if_block[0]
        false_label = else_block[0]
        try:
            condition = random.choice(context.get_statements(
                lambda s: not isinstance(s, Untyped) and isinstance(s.type, OpTypeBool)
            ))
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

#     def fuzz(self, context: "Context") -> List[OpCode]:
#         if context.get_depth() > context.config.max_depth:
#             return []
#         self.merge_label = OpLabel().fuzz(context)[0]
#         self.selection_control = None  # TODO
#         loop_label = OpLabel().fuzz(context)[0]
#         block = fuzz_block(context, loop_label)
#         try:
#             condition = random.choice(context.get_statements(
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
#     case_labels: List[OpLabel] = None
#     value: OpCode = None

#     def fuzz(self, context: "Context") -> Tuple[OpCode]:
#         if context.get_depth() > context.config.max_depth:
#             return []
#         self.selection_control = random.choice(list(SelectionControlMask))
#         self.default_label = OpLabel().fuzz(context)[0]
#         self.case_labels = []
#         for _ in range(random.randint(1, 5)):
#             self.case_labels.append(OpLabel().fuzz(context)[0])
#         self.value = random.choice(context.get_statements(
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


def fuzz_block(context: "Context", exit_label: Optional[OpLabel]) -> Tuple[OpCode]:
    block_label: OpLabel = OpLabel().fuzz(context)[0]
    instructions: List[OpCode] = []
    variables: List[OpVariable] = []
    block_context = context.make_child_context()
    import langspec.opcodes.arithmetic
    import langspec.opcodes.logic
    import langspec.opcodes.bitwise

    while random.random() < context.config.p_statement:
        opcodes: List[OpCode] = Statement().fuzz(block_context)
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
