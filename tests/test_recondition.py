import copy
import unittest

from run import SPIRVSmithConfig
from src import FuzzDelegator
from src.constants import OpConstantComposite
from src.context import Context
from src.enums import ExecutionModel
from src.monitor import Monitor
from src.operators.arithmetic.scalar_arithmetic import OpSMod
from src.operators.composite import OpVectorExtractDynamic
from src.recondition import recondition
from src.types.concrete_types import OpTypeInt
from src.types.concrete_types import OpTypeVector


config = SPIRVSmithConfig()
init_strategy = copy.deepcopy(config.strategy)
init_limits = copy.deepcopy(config.limits)

config.misc.broadcast_generated_shaders = False
config.misc.start_web_server = False
config.misc.upload_logs = False
monitor = Monitor(config)


class TestRecondition(unittest.TestCase):
    def setUp(self):
        FuzzDelegator.reset_parametrizations()
        config.limits = copy.deepcopy(init_limits)
        config.strategy = copy.deepcopy(init_strategy)
        self.context: Context = Context.create_global_context(
            ExecutionModel.GLCompute, config
        )

    def test_vector_access_is_reconditioned(self):
        int_type = OpTypeInt(32, 1)
        vec_type = OpTypeVector(int_type, 4)

        self.context.tvc[int_type] = int_type.id
        self.context.tvc[vec_type] = vec_type.id

        index = self.context.create_on_demand_numerical_constant(
            OpTypeInt, value=5, signed=1, width=32
        )
        vec_constant = OpConstantComposite(
            vec_type, tuple([index for _ in range(len(vec_type))])
        )

        self.context.tvc[vec_constant] = vec_constant.id
        self.context.tvc[index] = index.id

        vec_access = OpVectorExtractDynamic(int_type, vec_constant, index)

        opcodes = [int_type, vec_type, index, vec_constant, vec_access]

        reconditioned = recondition(self.context, opcodes)

        # We should have an extra OpSMod
        self.assertEqual(len(reconditioned), 6)
        self.assertTrue(isinstance(reconditioned[4], OpSMod))
        self.assertEqual(reconditioned[4].type, int_type)
        self.assertEqual(vec_access.index, reconditioned[4])

    def test_two_vector_accesses_are_reconditioned(self):
        int_type = OpTypeInt(32, 1)
        vec_type = OpTypeVector(int_type, 4)

        self.context.tvc[int_type] = int_type.id
        self.context.tvc[vec_type] = vec_type.id

        index = self.context.create_on_demand_numerical_constant(
            OpTypeInt, value=5, signed=1, width=32
        )
        vec_constant = OpConstantComposite(
            vec_type, tuple([index for _ in range(len(vec_type))])
        )

        self.context.tvc[vec_constant] = vec_constant.id
        self.context.tvc[index] = index.id

        vec_access1 = OpVectorExtractDynamic(int_type, vec_constant, index)

        vec_access2 = OpVectorExtractDynamic(int_type, vec_constant, index)

        opcodes = [int_type, vec_type, index, vec_constant, vec_access1, vec_access2]

        reconditioned = recondition(self.context, opcodes)

        self.assertEqual(len(reconditioned), 8)
        self.assertTrue(isinstance(reconditioned[4], OpSMod))
        self.assertTrue(isinstance(reconditioned[6], OpSMod))
        self.assertEqual(reconditioned[4].type, int_type)
        self.assertEqual(vec_access1.index, reconditioned[4])
        self.assertEqual(reconditioned[6].type, int_type)
        self.assertEqual(vec_access2.index, reconditioned[6])
