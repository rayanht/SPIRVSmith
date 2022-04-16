from src.enums import StorageClass
from src.types.abstract_types import ArithmeticType
from src.types.concrete_types import (
    OpTypeArray,
    OpTypeBool,
    OpTypeFloat,
    OpTypeInt,
    OpTypeMatrix,
    OpTypeStruct,
    OpTypeVector,
)

IsVectorType = lambda x: isinstance(x.type, OpTypeVector)
IsArrayType = lambda x: isinstance(x.type, OpTypeArray)
IsMatrixType = lambda x: isinstance(x.type, OpTypeMatrix)
IsStructType = lambda x: isinstance(x.type, OpTypeStruct)
IsScalarInteger = lambda x: isinstance(x.type, OpTypeInt)
IsScalarFloat = lambda x: isinstance(x.type, OpTypeFloat)
IsCompositeType = lambda x: isinstance(x.type, (OpTypeMatrix, OpTypeVector, OpTypeStruct, OpTypeArray))
HasValidBaseType = lambda x, target_type: isinstance(x.get_base_type(), target_type)
HasValidSign = (
    lambda x, signed: x.get_base_type().signed == signed if signed is not None else True
)
HasValidBaseTypeAndSign = lambda x, target_type, signed: HasValidBaseType(
    x, target_type
) and HasValidSign(x, signed)
HasValidType = lambda x, target_type: isinstance(x.type, target_type)
HasValidTypeAndSign = lambda x, target_type, signed: HasValidType(
    x, target_type
) and HasValidSign(x, signed)
HaveSameTypeLength = lambda x, y: len(x.type) == len(y.type)
IsNotOutputVariable = lambda x: not x.storage_class == StorageClass.Output
IsNotInputVariable = lambda x: not x.storage_class == StorageClass.Input
IsValidArithmeticOperand = lambda x: isinstance(x.type, ArithmeticType)
IsValidLogicalOperand = lambda x: isinstance(x.type, (OpTypeBool, ArithmeticType))
IsValidBitwiseOperand = lambda x: isinstance(x.type, ArithmeticType)
IsConversionOperand = lambda x: isinstance(x.type, ArithmeticType)
