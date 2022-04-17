import copy
import unittest
from src import FuzzDelegator, Type
from src.constants import OpConstant, OpConstantComposite
from src.monitor import Monitor
from src.enums import ExecutionModel
from src.context import Context
from run_local import SPIRVSmithConfig
from src.predicates import HaveSameBaseType, HaveSameType
from src.types.concrete_types import OpTypeFloat, OpTypeInt, OpTypeVector

N = 1000
monitor = Monitor()
config = SPIRVSmithConfig()
init_strategy = copy.deepcopy(config.strategy)
init_limits = copy.deepcopy(config.limits)

config.misc.broadcast_generated_shaders = False
config.misc.start_web_server = False


def create_vector_const(
    context: Context, inner_type: Type, size: int = 4, value: int = 42
):
    const: OpConstant = context.create_on_demand_numerical_constant(
        inner_type, value=value, width=32
    )

    vector_type = OpTypeVector()
    vector_type.type = const.type
    vector_type.size = size
    context.add_to_tvc(vector_type)

    vector_const = OpConstantComposite()
    vector_const.type = vector_type
    vector_const.constituents = tuple([const for _ in range(size)])
    context.add_to_tvc(vector_const)
    return vector_const


class TestArithmetic(unittest.TestCase):
    def setUp(self):
        FuzzDelegator.reset_parametrizations()
        config.limits = copy.deepcopy(init_limits)
        config.strategy = copy.deepcopy(init_strategy)
        self.context: Context = Context.create_global_context(
            ExecutionModel.GLCompute, config, monitor
        )

    def test_ints_same_width_and_signedness_are_equal(self):
        const1: OpConstant = self.context.create_on_demand_numerical_constant(
            OpTypeInt, value=42, width=32, signed=0
        )
        const2: OpConstant = self.context.create_on_demand_numerical_constant(
            OpTypeInt, value=69, width=32, signed=0
        )

        self.assertEqual(const1.type, const2.type)
        self.assertTrue(HaveSameType(const1, const2))

        const3: OpConstant = self.context.create_on_demand_numerical_constant(
            OpTypeInt, value=42, width=32, signed=1
        )
        const4: OpConstant = self.context.create_on_demand_numerical_constant(
            OpTypeInt, value=69, width=32, signed=1
        )

        self.assertEqual(const3.type, const4.type)
        self.assertTrue(HaveSameType(const3, const4))

        self.assertNotEqual(const1.type, const3.type)
        self.assertNotEqual(const2.type, const4.type)

        self.assertFalse(HaveSameType(const1, const3))
        self.assertFalse(HaveSameType(const2, const4))

    def test_floats_same_width_are_equal(self):
        const1: OpConstant = self.context.create_on_demand_numerical_constant(
            OpTypeFloat, value=42, width=32
        )
        const2: OpConstant = self.context.create_on_demand_numerical_constant(
            OpTypeFloat, value=69, width=32
        )

        self.assertEqual(const1.type, const2.type)
        self.assertTrue(HaveSameType(const1, const2))

    def test_vectors_same_size_and_base_type_are_equal(self):
        vec_const1: OpConstantComposite = create_vector_const(
            self.context, OpTypeInt, size=4, value=42
        )
        vec_const2: OpConstantComposite = create_vector_const(
            self.context, OpTypeInt, size=4, value=69
        )

        self.assertEqual(vec_const1.type, vec_const2.type)
        self.assertTrue(HaveSameType(vec_const1, vec_const2))
        self.assertTrue(HaveSameBaseType(vec_const1, vec_const2))

    def test_vectors_same_size_and_different_base_type_are_not_equal(self):
        vec_const1: OpConstantComposite = create_vector_const(
            self.context, OpTypeInt, 4, value=42
        )
        vec_const2: OpConstantComposite = create_vector_const(
            self.context, OpTypeFloat, 4, value=69
        )

        self.assertNotEqual(vec_const1.type, vec_const2.type)
        self.assertFalse(HaveSameType(vec_const1, vec_const2))
        self.assertFalse(HaveSameBaseType(vec_const1, vec_const2))

    def test_vectors_different_size_and_same_base_type_are_not_equal(self):
        vec_const1: OpConstantComposite = create_vector_const(
            self.context, OpTypeInt, 2, value=42
        )
        vec_const2: OpConstantComposite = create_vector_const(
            self.context, OpTypeInt, 4, value=69
        )

        self.assertNotEqual(vec_const1.type, vec_const2.type)
        self.assertFalse(HaveSameType(vec_const1, vec_const2))
        self.assertTrue(HaveSameBaseType(vec_const1, vec_const2))
