import copy
import unittest

from omegaconf import OmegaConf
from spirv_enums import ExecutionModel

from run import SPIRVSmithConfig
from src import FuzzDelegator
from src.constants import OpConstant
from src.constants import OpConstantComposite
from src.context import Context
from src.monitor import Monitor
from src.operators.arithmetic.linear_algebra import (
    OpOuterProduct,
)
from src.operators.composite import OpCompositeExtract
from src.operators.composite import OpCompositeInsert
from src.operators.composite import OpTranspose
from src.operators.composite import OpVectorExtractDynamic
from src.operators.composite import OpVectorInsertDynamic
from src.types.concrete_types import OpTypeFloat
from src.types.concrete_types import OpTypeInt
from tests import create_vector_const

N = 1000

config: SPIRVSmithConfig = OmegaConf.structured(SPIRVSmithConfig())
init_strategy = copy.deepcopy(config.strategy)
init_limits = copy.deepcopy(config.limits)

config.misc.broadcast_generated_shaders = False
config.misc.upload_logs = False
monitor = Monitor(config)


class TestComposite(unittest.TestCase):
    def setUp(self):
        FuzzDelegator.reset_parametrizations()
        config.limits = copy.deepcopy(init_limits)
        config.strategy = copy.deepcopy(init_strategy)
        self.context: Context = Context.create_global_context(
            ExecutionModel.GLCompute, config
        )

    def test_vector_dynamic_extract_has_correct_type(self):
        index_const: OpConstant = self.context.create_on_demand_numerical_constant(
            OpTypeInt
        )
        vec_const: OpConstantComposite = create_vector_const(self.context, OpTypeFloat)
        vector_extract: OpVectorExtractDynamic = OpVectorExtractDynamic.fuzz(
            self.context
        ).opcode

        self.assertEqual(vector_extract.type, vec_const.get_base_type())
        self.assertEqual(vector_extract.index, index_const)

    def test_vector_insert_preserves_type(self):
        index_const: OpConstant = self.context.create_on_demand_numerical_constant(
            OpTypeInt
        )
        vec_const: OpConstantComposite = create_vector_const(self.context, OpTypeFloat)

        vector_insert: OpVectorInsertDynamic = OpVectorInsertDynamic.fuzz(
            self.context
        ).opcode

        self.assertEqual(vector_insert.type, vec_const.type)
        self.assertEqual(vector_insert.index, index_const)

    def test_composite_extract_has_correct_type(self):
        vec_const: OpConstantComposite = create_vector_const(self.context, OpTypeFloat)

        vector_extract: OpCompositeExtract = OpCompositeExtract.fuzz(
            self.context
        ).opcode

        self.assertEqual(vector_extract.type, vec_const.get_base_type())

    def test_composite_insert_preserves_type(self):
        vec_const: OpConstantComposite = create_vector_const(self.context, OpTypeFloat)

        vector_insert: OpCompositeInsert = OpCompositeInsert.fuzz(self.context).opcode

        self.assertEqual(vector_insert.type, vec_const.type)

    def test_transpose_has_correct_shape(self):
        create_vector_const(self.context, OpTypeFloat, size=4)
        create_vector_const(self.context, OpTypeFloat, size=2)

        outer_product: OpOuterProduct = OpOuterProduct.fuzz(self.context).opcode
        self.context.symbol_table.append(outer_product)

        transpose: OpTranspose = OpTranspose.fuzz(self.context).opcode

        self.assertEqual(len(transpose.type), len(outer_product.type.type))
        self.assertEqual(len(transpose.type.type), len(outer_product.type))
