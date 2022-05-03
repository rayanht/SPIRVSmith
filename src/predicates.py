from src import Untyped
from src.enums import StorageClass
from src.types.concrete_types import OpTypeArray
from src.types.concrete_types import OpTypeFloat
from src.types.concrete_types import OpTypeInt
from src.types.concrete_types import OpTypeMatrix
from src.types.concrete_types import OpTypePointer
from src.types.concrete_types import OpTypeStruct
from src.types.concrete_types import OpTypeVector

And = lambda *ps: lambda x: all(p(x) for p in ps)
Or = lambda *ps: lambda x: any(p(x) for p in ps)
Not = lambda p: lambda x: not p(x)

HasType = lambda t: lambda x: x.type == t
HasBaseType = lambda t: lambda x: x.get_base_type() == t
HasLength = lambda n: lambda x: len(x.type) == n
IsOfType = lambda t: lambda x: isinstance(x.type, t)
IsOfBaseType = lambda t: lambda x: isinstance(x.get_base_type(), t)

IsTyped = lambda x: not isinstance(x, Untyped)

IsSigned = lambda x: x.signed == 1

IsBaseTypeSigned = lambda x: IsSigned(x.get_base_type())
IsBaseTypeUnsigned = lambda x: Not(IsSigned)(x.get_base_type())

IsOfFloatBaseType = IsOfBaseType(OpTypeFloat)
IsOfUnsignedIntegerBaseType = And(IsOfBaseType(OpTypeInt), IsBaseTypeUnsigned)
IsOfSignedIntegerBaseType = And(IsOfBaseType(OpTypeInt), IsBaseTypeSigned)

IsVectorType = IsOfType(OpTypeVector)
IsArrayType = IsOfType(OpTypeArray)
IsMatrixType = IsOfType(OpTypeMatrix)
IsStructType = IsOfType(OpTypeStruct)
IsPointerType = IsOfType(OpTypePointer)
IsCompositeType = IsOfType((OpTypeMatrix, OpTypeVector, OpTypeStruct, OpTypeArray))

IsScalarInteger = IsOfType(OpTypeInt)
IsScalarFloat = IsOfType(OpTypeFloat)

IsScalarUnsignedInteger = And(IsScalarInteger, Not(IsBaseTypeSigned))
IsScalarSignedInteger = And(IsScalarInteger, IsBaseTypeSigned)

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

IsOutputVariable = lambda x: x.storage_class == StorageClass.Output
IsInputVariable = lambda x: x.storage_class == StorageClass.Input
