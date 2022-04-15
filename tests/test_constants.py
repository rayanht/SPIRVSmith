import copy
from dataclasses import replace
import unittest
from src import FuzzDelegator
from src.constants import OpConstant, OpConstantFalse, OpConstantTrue
from src.memory import OpLoad
from src.monitor import Monitor
from src.enums import ExecutionModel, StorageClass
from src.context import Context
from run_local import SPIRVSmithConfig
from src.types.concrete_types import OpTypeBool, OpTypeInt

N = 1000
monitor = Monitor()
config = SPIRVSmithConfig()
init_strategy = copy.deepcopy(config.strategy)
init_limits = copy.deepcopy(config.limits)

config.misc.broadcast_generated_shaders = False
config.misc.start_web_server = False


class TestMemory(unittest.TestCase):
    def setUp(self):
        FuzzDelegator.reset_parametrizations()
        config.limits = copy.deepcopy(init_limits)
        config.strategy = copy.deepcopy(init_strategy)
        self.context: Context = Context.create_global_context(
            ExecutionModel.GLCompute, config, monitor
        )

    def test_fuzzing_bool_constants(self):
        bool_constant1 = OpConstantTrue().fuzz(self.context)
        bool_constant2 = OpConstantFalse().fuzz(self.context)
        self.assertEqual(bool_constant1[0], OpTypeBool())
        self.assertEqual(bool_constant2[0], OpTypeBool())

    def test_fuzzing_numerical_constants_montecarlo(self):
        signedness_counter = {0: 0, 1: 0}
        constants = []
        for _ in range(N):
            const = OpConstant().fuzz(self.context)[-1]
            if isinstance(const.type, OpTypeInt):
                signedness_counter[const.type.signed] += 1
            constants.append(const)
        M = len(list(filter(lambda c: isinstance(c.type, OpTypeInt), constants)))
        # About half of ints are signed, and the other half are unsigned
        self.assertAlmostEqual(signedness_counter[0], M // 2, delta=M // 10)
        # Almost as many floats as ints
        self.assertAlmostEqual(N - M, M, delta=(N - M) // 10)
        # All unsigned ints are positive
        self.assertTrue(
            all(
                [
                    c.value >= 0
                    for c in constants
                    if isinstance(c.type, OpTypeInt) and not c.type.signed
                ]
            )
        )
