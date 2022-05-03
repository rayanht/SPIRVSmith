from types import NoneType
from typing import get_args
from typing import Optional
from typing import TYPE_CHECKING

from src import Constant
from src import OpCode
from src import Signed
from src import Statement
from src.constants import OpConstantComposite

if TYPE_CHECKING:
    from src.context import Context
from src.extension import OpExtInst
from src.types.concrete_types import OpTypeVector

Operand = Statement | Constant


class GLSLExtensionOperator:
    ...


class UnaryOperatorFuzzMixin:
    def fuzz(self, context: "Context") -> list[OpCode]:
        (
            source_type,
            destination_type,
            source_constraint,
            destination_constraint,
        ) = get_args(self.__class__.__orig_bases__[1])
        source_signed = None
        if not issubclass(source_constraint, NoneType):
            source_signed = issubclass(source_constraint, Signed)
        destination_signed = None
        if not issubclass(destination_constraint, NoneType):
            destination_signed = issubclass(destination_constraint, Signed)
        operand: Optional[Operand] = context.get_random_operand(
            self.OPERAND_SELECTION_PREDICATE(source_type, source_signed)
        )
        if operand is None:
            return []
        if not issubclass(destination_type, NoneType):
            inner_type = destination_type().fuzz(context)[-1]
            if destination_signed is not None:
                inner_type.signed = int(destination_signed)
            context.add_to_tvc(inner_type)
            # if isinstance(operand, OpConstantComposite):
            #     inner_type.width = operand.type.type.width
            if hasattr(operand, "width"):
                inner_type.width = operand.get_base_type().width
            if isinstance(operand.type, (OpConstantComposite, OpTypeVector)):
                self.type = OpTypeVector().fuzz(context)[-1]
                self.type.type = inner_type
                self.type.size = len(operand.type)
                context.add_to_tvc(self.type)
            else:
                self.type = inner_type
        else:
            self.type = operand.type
        self.operand1 = operand
        if isinstance(self, GLSLExtensionOperator):
            return [
                OpExtInst(
                    type=self.type,
                    extension_set=context.extension_sets["GLSL"],
                    instruction=self.__class__,
                    operands=tuple([self.operand1]),
                )
            ]
        return [self]

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.operand1})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.operand1})"


class BinaryOperatorFuzzMixin:
    def fuzz(self, context: "Context") -> list[OpCode]:
        (
            source_type,
            destination_type,
            source_constraint,
            destination_constraint,
        ) = get_args(self.__class__.__orig_bases__[1])
        source_signed = None
        if not issubclass(source_constraint, NoneType):
            source_signed = issubclass(source_constraint, Signed)
        destination_signed = None
        if not issubclass(destination_constraint, NoneType):
            destination_signed = issubclass(destination_constraint, Signed)
        operand1: Optional[Operand] = context.get_random_operand(
            self.OPERAND_SELECTION_PREDICATE(source_type, source_signed)
        )
        if operand1 is None:
            return []
        operand2: Optional[Operand] = context.get_random_operand(
            self.OPERAND_SELECTION_PREDICATE(source_type, source_signed),
            constraint=operand1,
        )
        if operand2 is None:
            return []
        if not issubclass(destination_type, NoneType):
            inner_type = destination_type().fuzz(context)[-1]
            if destination_signed is not None:
                inner_type.signed = int(destination_signed)
            context.add_to_tvc(inner_type)
            # if isinstance(operand, OpConstantComposite):
            #     inner_type.width = operand.type.type.width
            if hasattr(operand1, "width"):
                inner_type.width = operand1.get_base_type().width
            if isinstance(operand1.type, (OpConstantComposite, OpTypeVector)):
                self.type = OpTypeVector().fuzz(context)[-1]
                self.type.type = inner_type
                self.type.size = len(operand1.type)
                context.add_to_tvc(self.type)
            else:
                self.type = inner_type
        else:
            self.type = operand1.type
        self.operand1 = operand1
        self.operand2 = operand2
        if isinstance(self, GLSLExtensionOperator):
            return [
                OpExtInst(
                    type=self.type,
                    extension_set=context.extension_sets["GLSL"],
                    instruction=self.__class__,
                    operands=tuple([self.operand1, self.operand2]),
                )
            ]
        return [self]

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.operand1})({self.operand2})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.operand1})({self.operand2})"
