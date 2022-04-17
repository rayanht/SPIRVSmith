import copy
import unittest
from src import FuzzDelegator, Type
from src.constants import (
    OpConstant,
    OpConstantComposite,
)
from src.monitor import Monitor
from src.enums import ExecutionModel
from src.context import Context
from run_local import SPIRVSmithConfig
from src.operators.arithmetic.linear_algebra import (
    OpMatrixTimesMatrix,
    OpMatrixTimesVector,
    OpOuterProduct,
    OpVectorTimesMatrix,
    OpVectorTimesScalar,
)
from src.operators.composite import OpCompositeExtract, OpCompositeInsert, OpTranspose, OpVectorExtractDynamic, OpVectorInsertDynamic
from src.types.concrete_types import OpTypeFloat, OpTypeInt, OpTypeVector

N = 1000
monitor = Monitor()
config = SPIRVSmithConfig()
init_strategy = copy.deepcopy(config.strategy)
init_limits = copy.deepcopy(config.limits)

config.misc.broadcast_generated_shaders = False
config.misc.start_web_server = False


def create_vector_const(context: Context, inner_type: Type, size: int = 4):
    const: OpConstant = context.create_on_demand_numerical_constant(
        inner_type, value=42, width=32
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

    def test_vector_dynamic_extract_has_correct_type(self):
        vec_const: OpConstantComposite = create_vector_const(self.context, OpTypeFloat)

        vector_extract: OpVectorExtractDynamic = OpVectorExtractDynamic().fuzz(
            self.context
        )[-1]

        self.assertEqual(vector_extract.type, vec_const.get_base_type())
    
    def test_vector_insert_preserves_type(self):
        vec_const: OpConstantComposite = create_vector_const(self.context, OpTypeFloat)

        vector_insert: OpVectorInsertDynamic = OpVectorInsertDynamic().fuzz(
            self.context
        )[-1]

        self.assertEqual(vector_insert.type, vec_const.type)

    def test_composite_extract_has_correct_type(self):
        vec_const: OpConstantComposite = create_vector_const(self.context, OpTypeFloat)

        vector_extract: OpCompositeExtract = OpCompositeExtract().fuzz(
            self.context
        )[-1]

        self.assertEqual(vector_extract.type, vec_const.get_base_type())

    def test_composite_insert_preserves_type(self):
        vec_const: OpConstantComposite = create_vector_const(self.context, OpTypeFloat)

        vector_insert: OpCompositeInsert = OpCompositeInsert().fuzz(
            self.context
        )[-1]

        self.assertEqual(vector_insert.type, vec_const.type)
        
    def test_transpose_has_correct_shape(self):
        create_vector_const(self.context, OpTypeFloat, size=4)
        create_vector_const(self.context, OpTypeFloat, size=2)

        outer_product: OpOuterProduct = OpOuterProduct().fuzz(self.context)[-1]
        self.context.symbol_table[outer_product] = outer_product.id
        
        transpose: OpTranspose = OpTranspose().fuzz(self.context)[-1]
        
        self.assertEqual(len(transpose.type), len(outer_product.type.type))
        self.assertEqual(len(transpose.type.type), len(outer_product.type))