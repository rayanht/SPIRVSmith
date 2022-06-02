import copy
import unittest

from omegaconf import OmegaConf
from spirv_enums import ExecutionModel

from run import SPIRVSmithConfig
from src import FuzzDelegator
from src import Type
from src.context import Context
from src.monitor import Monitor
from src.operators.arithmetic.scalar_arithmetic import OpISub
from src.predicates import IsArithmeticType
from src.types.abstract_types import MiscType
from src.types.abstract_types import ScalarType
from src.types.concrete_types import OpTypeBool
from src.types.concrete_types import OpTypeFloat
from src.types.concrete_types import OpTypeFunction
from src.types.concrete_types import OpTypeInt
from src.types.concrete_types import OpTypeVector

N = 500

config: SPIRVSmithConfig = OmegaConf.structured(SPIRVSmithConfig())
init_strategy = copy.deepcopy(config.strategy)
init_limits = copy.deepcopy(config.limits)

config.misc.broadcast_generated_shaders = False
config.misc.upload_logs = False
monitor = Monitor(config)


class TestContext(unittest.TestCase):
    def setUp(self):
        FuzzDelegator.reset_parametrizations()
        config.limits = copy.deepcopy(init_limits)
        config.strategy = copy.deepcopy(init_strategy)
        self.context: Context = Context.create_global_context(
            ExecutionModel.GLCompute, config
        )

    def test_context_registers_all_constants(self):
        self.context.create_on_demand_numerical_constant(OpTypeInt, value=0)
        self.context.create_on_demand_numerical_constant(OpTypeInt, value=1)

        self.assertEqual(
            len(list(self.context.get_constants(IsArithmeticType))),
            2,
        )

    def test_constants_of_same_value_and_type_should_be_conflated_int(self):
        constant1 = self.context.create_on_demand_numerical_constant(
            OpTypeInt, value=0, width=32, signed=0
        )
        constant2 = self.context.create_on_demand_numerical_constant(
            OpTypeInt, value=0, width=32, signed=0
        )

        self.assertTrue(
            len(list(self.context.get_constants(IsArithmeticType))),
            1,
        )
        self.assertEqual(constant1, constant2)

    def test_context_same_types_should_be_conflated_bool(self):
        self.context.add_to_tvc(OpTypeBool())
        self.context.add_to_tvc(OpTypeBool())

        self.assertEqual(len(self.context.globals), 1)

    def test_context_same_types_should_be_conflated_int(self):
        self.context.add_to_tvc(OpTypeInt(32, 1))
        self.context.add_to_tvc(OpTypeInt(32, 1))

        self.assertEqual(len(self.context.globals), 1)

    def test_context_same_types_should_be_conflated_vector(self):
        self.context.add_to_tvc(OpTypeVector(OpTypeInt(32, 1), 4))
        self.context.add_to_tvc(OpTypeVector(OpTypeInt(32, 1), 4))

        self.assertEqual(len(self.context.globals), 1)

    def test_context_finds_all_arithmetic_operands(self):
        constant1 = self.context.create_on_demand_numerical_constant(OpTypeInt, 0)
        constant2 = self.context.create_on_demand_numerical_constant(OpTypeInt, 1)

        operator = OpISub.fuzz(self.context).opcode

        self.assertTrue(
            operator.operand1 == constant1 or operator.operand1 == constant2
        )

    def test_context_finds_all_arithmetic_operands_monte_carlo(self):
        constant1 = self.context.create_on_demand_numerical_constant(OpTypeInt, 0)
        constant2 = self.context.create_on_demand_numerical_constant(OpTypeInt, 1)

        counter = {constant1: 0, constant2: 0}
        for _ in range(N):
            operator = OpISub.fuzz(self.context).opcode
            counter[operator.operand1] += 1
            counter[operator.operand2] += 1

        self.assertAlmostEqual(counter[constant1], N, delta=N // 10)
        self.assertAlmostEqual(counter[constant2], N, delta=N // 10)

    def test_depth_is_correct(self):
        context = self.context
        for _ in range(5):
            context = context.make_child_context(None)

        self.assertEqual(context.get_depth(), 6)

    def test_numerical_types_distributed_correctly(self):
        self.context.config.limits.n_types = N
        self.context.config.strategy.w_container_type = 0

        Type.parametrize(self.context)
        Type.set_zero_probability(MiscType, self.context)
        ScalarType.set_zero_probability(OpTypeBool, self.context)

        type1: Type = OpTypeInt(32, 0)
        type2: Type = OpTypeInt(32, 1)
        type3: Type = OpTypeFloat(32)

        counter = {type1: 0, type2: 0, type3: 0}

        types = [Type.fuzz(self.context).opcode for _ in range(N)]

        for type in types:
            counter[type] += 1

        self.assertAlmostEqual(counter[type1], N // 4, delta=N // 10)
        self.assertAlmostEqual(counter[type2], N // 4, delta=N // 10)
        self.assertAlmostEqual(counter[type3], N // 2, delta=N // 10)

    def test_correct_number_of_function_types_created(self):
        self.context.config.limits.n_types = N
        self.context.config.strategy.w_scalar_type = 1
        self.context.config.strategy.w_container_type = 1

        self.context.config.limits.n_functions = 5

        Type.parametrize(self.context)

        self.context.gen_types()

        self.assertEqual(MiscType.get_parametrization()[OpTypeFunction.__name__], 0)
        self.assertEqual(len(self.context.get_function_types()), 5)
