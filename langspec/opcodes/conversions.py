import random
from types import NoneType

from typing import (
    TYPE_CHECKING,
    Generic,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
    get_args,
)
from langspec.opcodes import OpCode, Signed, Statement, Unsigned

from langspec.opcodes.constants import Constant

if TYPE_CHECKING:
    from langspec.opcodes.context import Context
from langspec.opcodes.types.abstract_types import (
    NumericalType,
)
from langspec.opcodes.types.concrete_types import (
    OpTypeBool,
    OpTypeFloat,
    OpTypeInt,
    OpTypeVector,
    Type,
)

Operand = Statement | Constant


def find_conversion_operand(
    context: "Context",
    target_type: Type,
    signed: bool | NoneType,
) -> Operand:
    operands: List[Statement] = context.get_typed_statements(
        lambda _: True
    ) + context.get_constants((OpTypeInt, OpTypeVector))
    eligible_operands: List[Operand] = []
    for operand in operands:
        if isinstance(operand.type, target_type) or (
            isinstance(operand.type, OpTypeVector)
            and isinstance(operand.type.type, target_type)
        ):
            if (
                isinstance(operand.type, NumericalType)
                or isinstance(operand.type, OpTypeVector)
                and isinstance(operand.type.type, NumericalType)
            ):
                if signed is not None and operand.type.signed != signed:
                    continue
            eligible_operands.append(operand)
    if len(eligible_operands) == 0:
        return None
    return random.choice(eligible_operands)


S = TypeVar("S")
D = TypeVar("D")
SC = TypeVar("SC")
DC = TypeVar("DC")


class ConversionOperator(Statement, Generic[S, D, SC, DC]):
    ...


class ConversionOperatorFuzzMixin:
    def fuzz(self, context: "Context") -> List[OpCode]:
        (
            source_type,
            destination_type,
            source_constraint,
            destination_constraint,
        ) = get_args(self.__class__.__orig_bases__[1])
        source_signed = None
        if source_constraint != type(None):
            source_signed = source_constraint == type(Signed())
        destination_signed = None
        if destination_constraint != type(None):
            destination_signed = destination_constraint == type(Signed())
        self.operand = find_conversion_operand(context, source_type, source_signed)
        if not self.operand:
            return []
        inner_type = destination_type().fuzz(context)[-1]
        if destination_signed is not None:
            inner_type.signed = destination_signed
        inner_type.width = self.operand.type.width
        context.tvc[inner_type] = inner_type.id
        if isinstance(self.operand, OpTypeVector):
            self.type = OpTypeVector().fuzz(context)[-1]
            self.type.type = inner_type
            self.type.size = self.operand.size
            context.tvc[self.type] = self.type.id
        else:
            self.type = inner_type
        return [self]


class UnaryConversionOperator(ConversionOperator[S, D, Optional[SC], Optional[DC]]):
    type: Type = None
    operand: Operand = None

    def to_spasm(self, context: "Context") -> str:
        return f"%{self.id} = {self.__class__.__name__} %{context.tvc[self.type]} %{self.operand.id}"


class OpConvertFToU(
    ConversionOperatorFuzzMixin,
    UnaryConversionOperator[OpTypeFloat, OpTypeInt, None, Unsigned],
):
    ...


class OpConvertFToS(
    ConversionOperatorFuzzMixin,
    UnaryConversionOperator[OpTypeFloat, OpTypeInt, None, Signed],
):
    ...


class OpConvertSToF(
    ConversionOperatorFuzzMixin,
    UnaryConversionOperator[OpTypeInt, OpTypeFloat, Signed, None],
):
    ...


class OpConvertUToF(
    ConversionOperatorFuzzMixin,
    UnaryConversionOperator[OpTypeInt, OpTypeFloat, Unsigned, None],
):
    ...


# class OpUConvert(UnaryConversionOperator[OpTypeInt, Unsigned]):
#     ...
