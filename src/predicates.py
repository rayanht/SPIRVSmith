from src import Untyped
from src.enums import StorageClass
from src.operators.memory.variable import OpVariable
from src.types.abstract_types import ArithmeticType
from src.types.concrete_types import OpTypeArray
from src.types.concrete_types import OpTypeBool
from src.types.concrete_types import OpTypeFloat
from src.types.concrete_types import OpTypeInt
from src.types.concrete_types import OpTypeMatrix
from src.types.concrete_types import OpTypePointer
from src.types.concrete_types import OpTypeStruct
from src.types.concrete_types import OpTypeVector

And = lambda *ps: lambda x: all(p(x) for p in ps)
Or = lambda *ps: lambda x: any(p(x) for p in ps)
Not = lambda p: lambda x: not p(x)


IsTyped = lambda x: not isinstance(x, Untyped)
IsVariable = lambda x: isinstance(x, OpVariable)
HasFloatBaseType = lambda x: isinstance(x.get_base_type(), OpTypeFloat)
IsVectorType = lambda x: isinstance(x.type, OpTypeVector)
IsArrayType = lambda x: isinstance(x.type, OpTypeArray)
IsMatrixType = lambda x: isinstance(x.type, OpTypeMatrix)
IsStructType = lambda x: isinstance(x.type, OpTypeStruct)
IsScalarInteger = lambda x: isinstance(x.type, OpTypeInt)
IsScalarFloat = lambda x: isinstance(x.type, OpTypeFloat)
IsPointerType = lambda x: isinstance(x.type, OpTypePointer)

IsCompositeType = lambda x: isinstance(
    x.type, (OpTypeMatrix, OpTypeVector, OpTypeStruct, OpTypeArray)
)
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
HaveSameType = lambda x, y: x.type == y.type
HaveSameBaseType = lambda x, y: x.get_base_type() == y.get_base_type()

HasType = lambda t: lambda x: x.type == t
HasBaseType = lambda t: lambda x: x.get_base_type() == t
HasLength = lambda n: lambda x: len(x.type) == n

IsOutputVariable = lambda x: x.storage_class == StorageClass.Output
IsInputVariable = lambda x: x.storage_class == StorageClass.Input
IsValidArithmeticOperand = lambda x: isinstance(x.type, ArithmeticType)
IsValidLogicalOperand = lambda x: isinstance(x.type, (OpTypeBool, ArithmeticType))
IsValidBitwiseOperand = lambda x: isinstance(x.type, ArithmeticType)
IsConversionOperand = lambda x: isinstance(x.type, ArithmeticType)
