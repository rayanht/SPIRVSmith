import copy
import unittest
from src.monitor import Monitor
from src.recondition import recondition
from run_local import SPIRVSmithConfig
from src import FuzzDelegator
from src.constants import OpConstantComposite
from src.context import Context
from src.enums import ExecutionModel
from src.operators.arithmetic.scalar_arithmetic import OpSMod
from src.operators.composite import OpVectorExtractDynamic
from src.types.concrete_types import OpTypeInt, OpTypeVector

monitor = Monitor()
config = SPIRVSmithConfig()
init_strategy = copy.deepcopy(config.strategy)
init_limits = copy.deepcopy(config.limits)

config.misc.broadcast_generated_shaders = False
config.misc.start_web_server = False


class TestRecondition(unittest.TestCase):
    def setUp(self):
        FuzzDelegator.reset_parametrizations()
        config.limits = copy.deepcopy(init_limits)
        config.strategy = copy.deepcopy(init_strategy)
        self.context: Context = Context.create_global_context(
            ExecutionModel.GLCompute, config, monitor
        )

    def test_vector_access_is_reconditioned(self):
        int_type = OpTypeInt()
        int_type.width = 32
        int_type.signed = 1
        self.context.tvc[int_type] = int_type.id

        vec_type = OpTypeVector()
        vec_type.size = 4
        vec_type.type = int_type
        self.context.tvc[vec_type] = vec_type.id

        index = self.context.create_on_demand_numerical_constant(
            OpTypeInt, value=5, signed=1, width=32
        )
        self.context.tvc[index] = index.id

        vec_constant = OpConstantComposite()
        vec_constant.type = vec_type
        vec_constant.constituents = tuple([index for _ in range(len(vec_type))])
        self.context.tvc[vec_type] = vec_type.id

        vec_access = OpVectorExtractDynamic()
        vec_access.type = int_type
        vec_access.vector = vec_constant
        vec_access.index = index

        opcodes = [int_type, vec_type, index, vec_constant, vec_access]

        reconditioned = recondition(self.context, opcodes)

        # We should have an extra OpSMod
        self.assertEqual(len(reconditioned), 6)
        self.assertTrue(isinstance(reconditioned[4], OpSMod))
        self.assertEqual(reconditioned[4].type, int_type)
        self.assertEqual(vec_access.index, reconditioned[4])

    def test_two_vector_accesses_are_reconditioned(self):
        context: Context = Context.create_global_context(
            ExecutionModel.GLCompute, SPIRVSmithConfig(), monitor
        )

        int_type = OpTypeInt()
        int_type.width = 32
        int_type.signed = 1
        context.tvc[int_type] = int_type.id

        vec_type = OpTypeVector()
        vec_type.size = 4
        vec_type.type = int_type
        context.tvc[vec_type] = vec_type.id

        index = context.create_on_demand_numerical_constant(
            OpTypeInt, value=5, signed=1, width=32
        )
        context.tvc[index] = index.id

        vec_constant = OpConstantComposite()
        vec_constant.type = vec_type
        vec_constant.constituents = tuple([index for _ in range(len(vec_type))])
        context.tvc[vec_type] = vec_type.id

        vec_access1 = OpVectorExtractDynamic()
        vec_access1.type = int_type
        vec_access1.vector = vec_constant
        vec_access1.index = index

        vec_access2 = OpVectorExtractDynamic()
        vec_access2.type = int_type
        vec_access2.vector = vec_constant
        vec_access2.index = index

        opcodes = [int_type, vec_type, index, vec_constant, vec_access1, vec_access2]

        reconditioned = recondition(context, opcodes)

        self.assertEqual(len(reconditioned), 8)
        self.assertTrue(isinstance(reconditioned[4], OpSMod))
        self.assertTrue(isinstance(reconditioned[6], OpSMod))
        self.assertEqual(reconditioned[4].type, int_type)
        self.assertEqual(vec_access1.index, reconditioned[4])
        self.assertEqual(reconditioned[6].type, int_type)
        self.assertEqual(vec_access2.index, reconditioned[6])
