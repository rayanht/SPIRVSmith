from collections import Counter
from typing import Optional
import unittest
from monitor import Monitor
from src.enums import ExecutionModel
from src import PARAMETRIZATIONS, Type, members
from src.operators.arithmetic import OpISub
from src.constants import OpConstant
from src.context import Context
from run_local import SPIRVSmithConfig
from src.types.abstract_types import ArithmeticType, MixedContainerType, NumericalType
from src.types.concrete_types import (
    OpTypeBool,
    OpTypeFloat,
    OpTypeFunction,
    OpTypeInt,
    OpTypeVector,
    OpTypeVoid,
)

N = 500
monitor = Monitor()


class TestContext(unittest.TestCase):
    def test_context_registers_all_constants(self):
        context: Context = Context.create_global_context(
            ExecutionModel.GLCompute, SPIRVSmithConfig(), monitor
        )

        context.create_on_demand_numerical_constant(OpTypeInt, value=0)
        context.create_on_demand_numerical_constant(OpTypeInt, value=1)
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

        constant1 = context.create_on_demand_numerical_constant(
            OpTypeInt, value=0, width=32, signed=0
        )
        constant2 = context.create_on_demand_numerical_constant(
            OpTypeInt, value=0, width=32, signed=0
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
        self.assertEqual(constant1, constant2)

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

        self.assertEqual(len(context.tvc), 3)

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

        self.assertEqual(len(context.tvc), 4)

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

    def test_context_variables_in_different_scopes_should_not_be_conflated(self):
        pass

    def test_context_finds_all_arithmetic_operands(self):
        context: Context = Context.create_global_context(
            ExecutionModel.GLCompute, SPIRVSmithConfig(), monitor
        )

        constant1 = context.create_on_demand_numerical_constant(OpTypeInt, 0)
        constant2 = context.create_on_demand_numerical_constant(OpTypeInt, 1)

        operator = OpISub().fuzz(context)[-1]

        self.assertTrue(
            operator.operand1 == constant1 or operator.operand1 == constant2
        )

    def test_context_finds_all_arithmetic_operands_monte_carlo(self):
        context: Context = Context.create_global_context(
            ExecutionModel.GLCompute, SPIRVSmithConfig(), monitor
        )

        constant1 = context.create_on_demand_numerical_constant(OpTypeInt, 0)
        constant2 = context.create_on_demand_numerical_constant(OpTypeInt, 1)

        counter = {constant1: 0, constant2: 0}
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

    def test_numerical_types_distributed_correctly(self):
        context: Context = Context.create_global_context(
            ExecutionModel.GLCompute, SPIRVSmithConfig(), monitor
        )

        context.config.limits.n_types = N
        context.config.strategy.w_scalar_type = 0
        context.config.strategy.w_numerical_type = 1
        context.config.strategy.w_container_type = 0
        context.config.strategy.w_arithmetic_type = 0

        Type().parametrize(context)
        PARAMETRIZATIONS[Type.__name__][OpTypeVoid.__name__] = 0

        # All possible numerical types
        type1: Type = OpTypeInt().fuzz(context)[-1]
        type1.signed = 0

        type2: Type = OpTypeInt().fuzz(context)[-1]
        type2.signed = 1

        type3: Type = OpTypeFloat().fuzz(context)[-1]

        counter = {type1: 0, type2: 0, type3: 0}

        types = [Type().fuzz(context)[-1] for _ in range(N)]

        for type in types:
            counter[type] += 1

        self.assertAlmostEqual(counter[type1], N // 4, delta=N // 10)
        self.assertAlmostEqual(counter[type2], N // 4, delta=N // 10)
        self.assertAlmostEqual(counter[type3], N // 2, delta=N // 10)

    def test_correct_number_of_function_types_created(self):
        context: Context = Context.create_global_context(
            ExecutionModel.GLCompute, SPIRVSmithConfig(), monitor
        )

        context.config.limits.n_types = N
        context.config.strategy.w_scalar_type = 1
        context.config.strategy.w_numerical_type = 1
        context.config.strategy.w_container_type = 1
        context.config.strategy.w_arithmetic_type = 1

        context.config.limits.n_functions = 5

        Type().parametrize(context)

        context.gen_types()

        self.assertEqual(
            PARAMETRIZATIONS[MixedContainerType.__name__][OpTypeFunction.__name__], 0
        )
        self.assertEqual(len(context.get_function_types()), 5)
