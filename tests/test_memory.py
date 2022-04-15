import copy
from dataclasses import replace
import unittest
from src import FuzzDelegator
from src.memory import OpLoad
from src.monitor import Monitor
from src.enums import ExecutionModel, StorageClass
from src.context import Context
from run_local import SPIRVSmithConfig

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

    def test_opload_finds_global_variable(self):
        self.context.gen_types()
        variable = self.context.create_on_demand_variable(StorageClass.StorageBuffer)
        op_load: OpLoad = OpLoad().fuzz(self.context)[-1]
        self.assertEqual(op_load.variable, variable)
