import copy
import unittest

from omegaconf import OmegaConf
from spirv_enums import ExecutionModel

from run import SPIRVSmithConfig
from src import FuzzDelegator
from src.constants import OpConstant
from src.constants import OpConstantComposite
from src.context import Context
from src.misc import OpUndef
from src.monitor import Monitor
from src.operators.arithmetic.scalar_arithmetic import OpIAdd
from src.operators.arithmetic.scalar_arithmetic import OpSDiv
from src.operators.arithmetic.scalar_arithmetic import OpSMod
from src.operators.arithmetic.scalar_arithmetic import OpUDiv
from src.operators.composite import OpVectorExtractDynamic
from src.recondition import recondition_opcodes
from src.types.concrete_types import EmptyType
from src.types.concrete_types import OpTypeInt
from src.types.concrete_types import OpTypeVector


config: SPIRVSmithConfig = OmegaConf.structured(SPIRVSmithConfig())
init_strategy = copy.deepcopy(config.strategy)
init_limits = copy.deepcopy(config.limits)

config.misc.broadcast_generated_shaders = False
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

        self.context.add_to_tvc(int_type)
        self.context.add_to_tvc(vec_type)

        index = self.context.create_on_demand_numerical_constant(
            OpTypeInt, value=5, signed=1, width=32
        )
        vec_constant = OpConstantComposite(
            vec_type, tuple([index for _ in range(len(vec_type))])
        )

        self.context.add_to_tvc(vec_constant)
        self.context.add_to_tvc(index)

        vec_access = OpVectorExtractDynamic(int_type, vec_constant, index)

        opcodes = [vec_access]

        reconditioned = recondition_opcodes(self.context, opcodes)

        # We should have an extra OpSMod
        self.assertEqual(len(reconditioned), len(opcodes) + 1)
        self.assertTrue(
            isinstance(reconditioned[reconditioned.index(vec_access) - 1], OpSMod)
        )
        self.assertEqual(
            reconditioned[reconditioned.index(vec_access) - 1].type, int_type
        )
        self.assertEqual(
            vec_access.index, reconditioned[reconditioned.index(vec_access) - 1]
        )

    def test_two_vector_accesses_are_reconditioned(self):
        int_type = OpTypeInt(32, 1)
        vec_type = OpTypeVector(int_type, 4)

        self.context.add_to_tvc(int_type)
        self.context.add_to_tvc(vec_type)

        index = self.context.create_on_demand_numerical_constant(
            OpTypeInt, value=5, signed=1, width=32
        )
        vec_constant = OpConstantComposite(
            vec_type, tuple([index for _ in range(len(vec_type))])
        )

        self.context.add_to_tvc(vec_constant)
        self.context.add_to_tvc(index)

        vec_access1 = OpVectorExtractDynamic(int_type, vec_constant, index)

        vec_access2 = OpVectorExtractDynamic(int_type, vec_constant, index)

        opcodes = [index, vec_access1, vec_access2]

        reconditioned = recondition_opcodes(self.context, opcodes)

        self.assertEqual(len(reconditioned), len(opcodes) + 2)
        self.assertTrue(
            isinstance(reconditioned[reconditioned.index(vec_access1) - 1], OpSMod)
        )
        self.assertTrue(
            isinstance(reconditioned[reconditioned.index(vec_access2) - 1], OpSMod)
        )
        self.assertEqual(
            reconditioned[reconditioned.index(vec_access1) - 1].type, int_type
        )
        self.assertEqual(
            vec_access1.index, reconditioned[reconditioned.index(vec_access1) - 1]
        )
        self.assertEqual(
            reconditioned[reconditioned.index(vec_access2) - 1].type, int_type
        )
        self.assertEqual(
            vec_access2.index, reconditioned[reconditioned.index(vec_access2) - 1]
        )

    def test_multiple_reconditioning_rules_get_applied(self):
        int_type = OpTypeInt(32, 0)

        self.context.add_to_tvc(int_type)

        const_one = OpConstant(int_type, 1)
        const_zero = OpConstant(int_type, 1)

        self.context.add_to_tvc(const_one)
        self.context.add_to_tvc(const_zero)

        div = OpUDiv(int_type, OpUndef(EmptyType()), const_one)

        opcodes = [div]

        reconditioned = recondition_opcodes(self.context, opcodes)

        self.assertEqual(len(reconditioned), len(opcodes) + 1)
        self.assertTrue(isinstance(reconditioned[reconditioned.index(div) - 1], OpIAdd))
        self.assertTrue(div.operand1 == const_one or div.operand1 == const_zero)
