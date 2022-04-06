from types import NoneType
from typing import Optional, get_args
from src import Constant, OpCode, Signed, Statement
from src.constants import OpConstantComposite
from src.context import Context
from src.types.concrete_types import OpTypeVector

Operand = Statement | Constant


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
        self.operand: Optional[Operand] = context.get_random_operand(
            self.OPERAND_SELECTION_PREDICATE(source_type, source_signed)
        )
        if not self.operand:
            return []
        if not issubclass(destination_type, NoneType):
            inner_type = destination_type().fuzz(context)[-1]
            if destination_signed is not None:
                inner_type.signed = int(destination_signed)
            context.tvc[inner_type] = inner_type.id
            # if isinstance(self.operand, OpConstantComposite):
            #     inner_type.width = self.operand.type.type.width
            if hasattr(self.operand, "width"):
                inner_type.width = self.operand.get_base_type().width
            if isinstance(self.operand.type, (OpConstantComposite, OpTypeVector)):
                self.type = OpTypeVector().fuzz(context)[-1]
                self.type.type = inner_type
                self.type.size = len(self.operand.type)
                context.tvc[self.type] = self.type.id
            else:
                self.type = inner_type
            return [self]
        self.type = self.operand.type
        return [self]

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.type})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.type})"


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
        self.operand1: Optional[Operand] = context.get_random_operand(
            self.OPERAND_SELECTION_PREDICATE(source_type, source_signed)
        )
        if not self.operand1:
            return []
        self.operand2: Optional[Operand] = context.get_random_operand(
            self.OPERAND_SELECTION_PREDICATE(source_type, source_signed),
            constraint=self.operand1,
        )
        if not issubclass(destination_type, NoneType):
            inner_type = destination_type().fuzz(context)[-1]
            if destination_signed is not None:
                inner_type.signed = int(destination_signed)
            context.tvc[inner_type] = inner_type.id
            # if isinstance(self.operand, OpConstantComposite):
            #     inner_type.width = self.operand.type.type.width
            if hasattr(self.operand1, "width"):
                inner_type.width = self.operand1.get_base_type().width
            if isinstance(self.operand1.type, (OpConstantComposite, OpTypeVector)):
                self.type = OpTypeVector().fuzz(context)[-1]
                self.type.type = inner_type
                self.type.size = len(self.operand1.type)
                context.tvc[self.type] = self.type.id
            else:
                self.type = inner_type
            return [self]
        self.type = self.operand1.type
        return [self]

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.type})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.type})"
