import copy
import unittest

from run import SPIRVSmithConfig
from src import FuzzDelegator
from src.constants import OpConstant
from src.constants import OpConstantFalse
from src.constants import OpConstantTrue
from src.context import Context
from src.enums import ExecutionModel
from src.monitor import Monitor
from src.types.concrete_types import OpTypeBool
from src.types.concrete_types import OpTypeInt

N = 5000

config = SPIRVSmithConfig()
init_strategy = copy.deepcopy(config.strategy)
init_limits = copy.deepcopy(config.limits)

config.misc.broadcast_generated_shaders = False
config.misc.start_web_server = False
config.misc.upload_logs = False
monitor = Monitor(config)


class TestConstants(unittest.TestCase):
    def setUp(self):
        FuzzDelegator.reset_parametrizations()
        config.limits = copy.deepcopy(init_limits)
        config.strategy = copy.deepcopy(init_strategy)
        self.context: Context = Context.create_global_context(
            ExecutionModel.GLCompute, config
        )

    def test_fuzzing_bool_constants(self):
        bool_constant1 = OpConstantTrue.fuzz(self.context)
        bool_constant2 = OpConstantFalse.fuzz(self.context)
        self.assertEqual(bool_constant1.opcode.type, OpTypeBool())
        self.assertEqual(bool_constant2.opcode.type, OpTypeBool())

    def test_fuzzing_numerical_constants_montecarlo(self):
        signedness_counter = {0: 0, 1: 0}
        constants = []
        for _ in range(N):
            const = OpConstant.fuzz(self.context).opcode
            if isinstance(const.type, OpTypeInt):
                signedness_counter[const.type.signed] += 1
            constants.append(const)
        M = len(list(filter(lambda c: isinstance(c.type, OpTypeInt), constants)))
        # About half of ints are signed, and the other half are unsigned
        self.assertAlmostEqual(signedness_counter[0], M // 2, delta=M // 10)
        # Almost as many floats as ints
        self.assertAlmostEqual(N - M, M, delta=N // 10)
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
