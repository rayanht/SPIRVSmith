from types import NoneType
from typing import get_args
from typing import TYPE_CHECKING

from typing_extensions import Self

from src import Constant
from src import FuzzResult
from src import Signed
from src import Statement
from src.constants import OpConstantComposite
from src.predicates import HasType

if TYPE_CHECKING:
    from src.context import Context

from src.extension import OpExtInst
from src.types.concrete_types import OpTypeVector

Operand = Statement | Constant


class GLSLExtensionOperator:
    ...


class UnaryOperatorFuzzMixin:
    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        (
            source_type,
            destination_type,
            source_constraint,
            destination_constraint,
        ) = get_args(cls.__orig_bases__[1])
        source_signed: bool = None
        if not issubclass(source_constraint, NoneType):
            source_signed: bool = issubclass(source_constraint, Signed)
        destination_signed = None
        if not issubclass(destination_constraint, NoneType):
            destination_signed = issubclass(destination_constraint, Signed)
        operand: Operand = context.get_random_operand(
            cls.OPERAND_SELECTION_PREDICATE(source_type, source_signed)
        )
        if not issubclass(destination_type, NoneType):
            inner_type = destination_type.fuzz(context).opcode
            if destination_signed is not None:
                inner_type.signed = int(destination_signed)
            context.add_to_tvc(inner_type)
            # if isinstance(operand, OpConstantComposite):
            #     inner_type.width = operand.type.type.width
            if hasattr(operand, "width"):
                inner_type.width = operand.get_base_type().width
            if isinstance(operand.type, (OpConstantComposite, OpTypeVector)):
                inner_type = OpTypeVector(type=inner_type, size=len(operand.type))
                context.add_to_tvc(inner_type)
        else:
            inner_type = operand.type
        if issubclass(cls, GLSLExtensionOperator):
            return FuzzResult(
                OpExtInst(
                    type=inner_type,
                    extension_set=context.extension_sets["GLSL.std.450"],
                    instruction=cls,
                    operands=(operand,),
                )
            )
        return FuzzResult(cls(type=inner_type, operand1=operand), [inner_type])


class BinaryOperatorFuzzMixin:
    @classmethod
    def fuzz(cls, context: "Context") -> FuzzResult[Self]:
        (
            source_type,
            destination_type,
            source_constraint,
            destination_constraint,
        ) = get_args(cls.__orig_bases__[1])
        source_signed = None
        if not issubclass(source_constraint, NoneType):
            source_signed = issubclass(source_constraint, Signed)
        destination_signed = None
        if not issubclass(destination_constraint, NoneType):
            destination_signed = issubclass(destination_constraint, Signed)
        operand1: Operand = context.get_random_operand(
            cls.OPERAND_SELECTION_PREDICATE(source_type, source_signed)
        )
        operand2: Operand = context.get_random_operand(HasType(operand1.type))
        if not issubclass(destination_type, NoneType):
            inner_type = destination_type.fuzz(context).opcode
            if destination_signed is not None:
                inner_type.signed = int(destination_signed)
            context.add_to_tvc(inner_type)
            if hasattr(operand1, "width"):
                inner_type.width = operand1.get_base_type().width
            if isinstance(operand1.type, (OpConstantComposite, OpTypeVector)):
                inner_type = OpTypeVector(type=inner_type, size=len(operand1.type))
                context.add_to_tvc(inner_type)
        else:
            inner_type = operand1.type
        if issubclass(cls, GLSLExtensionOperator):
            return FuzzResult(
                OpExtInst(
                    type=inner_type,
                    extension_set=context.extension_sets["GLSL.std.450"],
                    instruction=cls,
                    operands=(operand1, operand2),
                )
            )
        return FuzzResult(
            cls(type=inner_type, operand1=operand1, operand2=operand2), [inner_type]
        )
