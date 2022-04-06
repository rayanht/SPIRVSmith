from src.types.abstract_types import ArithmeticType
from src.types.concrete_types import OpTypeBool, OpTypeFloat, OpTypeInt, OpTypeVector


HasValidBaseType = lambda x, target_type: isinstance(x.get_base_type(), target_type)
HasValidSign = (
    lambda x, signed: x.get_base_type().signed == signed if signed is not None else True
)
HasValidBaseTypeAndSign = lambda x, target_type, signed: HasValidBaseType(
    x, target_type
) and HasValidSign(x, signed)
HaveSameTypeLength = lambda x, y: len(x.type) == len(y.type)

IsValidArithmeticOperand = lambda x: isinstance(x.type, ArithmeticType)
IsValidLogicalOperand = lambda x: isinstance(x.type, (OpTypeBool, ArithmeticType))
IsValidBitwiseOperand = lambda x: isinstance(x.type, ArithmeticType)
IsConversionOperand = lambda x: isinstance(x.type, ArithmeticType)
