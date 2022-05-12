from src import Signed
from src import Unsigned
from src.operators import BinaryOperatorFuzzMixin
from src.operators import UnaryOperatorFuzzMixin
from src.operators.arithmetic import BinaryArithmeticOperator
from src.operators.arithmetic import UnaryArithmeticOperator
from src.patched_dataclass import dataclass
from src.types.concrete_types import OpTypeFloat
from src.types.concrete_types import OpTypeInt


@dataclass
class OpSNegate(
    UnaryOperatorFuzzMixin, UnaryArithmeticOperator[OpTypeInt, None, Signed, None]
):
    ...


@dataclass
class OpFNegate(
    UnaryOperatorFuzzMixin, UnaryArithmeticOperator[OpTypeFloat, None, None, None]
):
    ...


@dataclass
class OpIAdd(
    BinaryOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeInt, None, None, None]
):
    ...


@dataclass
class OpFAdd(
    BinaryOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeFloat, None, None, None]
):
    ...


@dataclass
class OpISub(
    BinaryOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeInt, None, None, None]
):
    ...


@dataclass
class OpFSub(
    BinaryOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeFloat, None, None, None]
):
    ...


@dataclass
class OpIMul(
    BinaryOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeInt, None, None, None]
):
    ...


@dataclass
class OpFMul(
    BinaryOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeFloat, None, None, None]
):
    ...


@dataclass
class OpUDiv(
    BinaryOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeInt, None, Unsigned, None]
):
    ...


@dataclass
class OpSDiv(
    BinaryOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeInt, None, Signed, None]
):
    ...


@dataclass
class OpFDiv(
    BinaryOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeFloat, None, None, None]
):
    ...


@dataclass
class OpUMod(
    BinaryOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeInt, None, Unsigned, None]
):
    ...


@dataclass
class OpSRem(
    BinaryOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeInt, None, Signed, None]
):
    ...


@dataclass
class OpSMod(
    BinaryOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeInt, None, Signed, None]
):
    ...


@dataclass
class OpFRem(
    BinaryOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeFloat, None, None, None]
):
    ...


@dataclass
class OpFMod(
    BinaryOperatorFuzzMixin, BinaryArithmeticOperator[OpTypeFloat, None, None, None]
):
    ...
