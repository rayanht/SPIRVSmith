from collections import Counter
from typing import Optional
import unittest
from monitor import Monitor
from src.enums import ExecutionModel
from src import Type, members
from src.operators.arithmetic import OpISub
from src.constants import OpConstant
from src.context import Context
from run_local import SPIRVSmithConfig
from src.types.abstract_types import ArithmeticType
from src.types.concrete_types import OpTypeBool, OpTypeFloat, OpTypeInt, OpTypeVector

N = 500
monitor = Monitor()

def create_numerical_constant_in_context(
    context: Context,
    target_type: Type,
    value: int = 0,
    width: int = 32,
    signed: Optional[int] = 0,
) -> OpTypeInt:
    type = target_type()
    type.width = width
    if signed:
        type.signed = signed
    constant = OpConstant().fuzz(context)[-1]
    constant.type = type
    constant.value = value
    context.tvc[type] = type.id
    context.tvc[constant] = constant.id
    return constant


def id_generator(i=1):
    while True:
        yield i
        i += 1


class TestContext(unittest.TestCase):
    def test_context_registers_all_constants(self):
        context: Context = Context.create_global_context(
            ExecutionModel.GLCompute, SPIRVSmithConfig(), monitor
        )

        create_numerical_constant_in_context(context, OpTypeInt, value=0)
        create_numerical_constant_in_context(context, OpTypeInt, value=1)
        self.assertTrue(
            len(
                list(
                    context.get_constants(
                        lambda sym: (isinstance(sym.type, ArithmeticType))
                    )
                )
            )
            == 2
        )

    def test_constants_of_same_value_and_type_should_be_conflated_int(self):
        context: Context = Context.create_global_context(
            ExecutionModel.GLCompute, SPIRVSmithConfig(), monitor
        )

        create_numerical_constant_in_context(
            context, OpTypeInt, value=0, width=32, signed=0
        )
        create_numerical_constant_in_context(
            context, OpTypeInt, value=0, width=32, signed=0
        )
        self.assertTrue(
            len(
                list(
                    context.get_constants(
                        lambda sym: (isinstance(sym.type, ArithmeticType))
                    )
                )
            )
            == 1
        )

    def test_context_same_types_should_be_conflated_bool(self):
        context: Context = Context.create_global_context(
            ExecutionModel.GLCompute, SPIRVSmithConfig(), monitor
        )

        bool_type1 = OpTypeBool()
        bool_type2 = OpTypeBool()

        context.tvc[bool_type1] = bool_type1.id
        context.tvc[bool_type2] = bool_type2.id

        self.assertTrue(len(context.tvc) == 3)

    def test_context_same_types_should_be_conflated_int(self):
        context: Context = Context.create_global_context(
            ExecutionModel.GLCompute, SPIRVSmithConfig(), monitor
        )

        int_type1 = OpTypeInt()
        int_type1.width = 32
        int_type1.signed = 1

        int_type2 = OpTypeInt()
        int_type2.width = 32
        int_type2.signed = 1

        context.tvc[int_type1] = int_type1.id
        context.tvc[int_type2] = int_type2.id

        self.assertTrue(len(context.tvc) == 3)

    def test_context_same_types_should_be_conflated_vector1(self):
        context: Context = Context.create_global_context(
            ExecutionModel.GLCompute, SPIRVSmithConfig(), monitor
        )

        int_type = OpTypeInt()
        int_type.width = 32
        int_type.signed = 1

        context.tvc[int_type] = int_type.id

        vec_type1 = OpTypeVector()
        vec_type1.size = 4
        vec_type1.type = int_type

        vec_type2 = OpTypeVector()
        vec_type2.size = 4
        vec_type2.type = int_type

        context.tvc[vec_type1] = vec_type1.id
        context.tvc[vec_type2] = vec_type2.id

        self.assertTrue(len(context.tvc) == 4)

    def test_context_same_types_should_be_conflated_vector2(self):
        context: Context = Context.create_global_context(
            ExecutionModel.GLCompute, SPIRVSmithConfig(), monitor
        )

        int_type1 = OpTypeInt()
        int_type1.width = 32
        int_type1.signed = 1

        int_type2 = OpTypeInt()
        int_type2.width = 32
        int_type2.signed = 1

        context.tvc[int_type1] = int_type1.id
        context.tvc[int_type2] = int_type2.id

        vec_type1 = OpTypeVector()
        vec_type1.size = 4
        vec_type1.type = int_type1

        vec_type2 = OpTypeVector()
        vec_type2.size = 4
        vec_type2.type = int_type2

        context.tvc[vec_type1] = vec_type1.id
        context.tvc[vec_type2] = vec_type2.id

        self.assertTrue(len(context.tvc) == 4)

    def test_context_finds_all_arithmetic_operands(self):
        context: Context = Context.create_global_context(
            ExecutionModel.GLCompute, SPIRVSmithConfig(), monitor
        )

        constant1 = create_numerical_constant_in_context(context, OpTypeInt, 0)
        constant2 = create_numerical_constant_in_context(context, OpTypeInt, 1)

        operator = OpISub().fuzz(context)[-1]

        self.assertTrue(
            operator.operand1 == constant1 or operator.operand1 == constant2
        )

    def test_context_finds_all_arithmetic_operands_monte_carlo(self):
        context: Context = Context.create_global_context(
            ExecutionModel.GLCompute, SPIRVSmithConfig(), monitor
        )

        constant1 = create_numerical_constant_in_context(context, OpTypeInt, 0)
        constant2 = create_numerical_constant_in_context(context, OpTypeInt, 1)

        counter = Counter()
        for _ in range(N):
            operator = OpISub().fuzz(context)[-1]
            counter[operator.operand1] += 1
            counter[operator.operand2] += 1

        # print(operand_count)
        self.assertAlmostEqual(counter[constant1], N, delta=N // 10)
        self.assertAlmostEqual(counter[constant2], N, delta=N // 10)

    def test_depth_is_correct(self):
        context: Context = Context.create_global_context(
            ExecutionModel.GLCompute, SPIRVSmithConfig(), monitor
        )

        for _ in range(5):
            context = context.make_child_context(None)

        self.assertTrue(context.get_depth() == 6)
