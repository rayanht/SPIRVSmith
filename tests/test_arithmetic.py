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
from src.types.concrete_types import OpTypeFloat, OpTypeVector

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

    def test_vector_times_scalar_preserves_type(self):
        const: OpConstant = create_vector_const(self.context, OpTypeFloat)

        vector_times_scalar: OpVectorTimesScalar = OpVectorTimesScalar().fuzz(
            self.context
        )[-1]

        self.assertEqual(vector_times_scalar.type, const.type)

    def test_outer_product_has_correct_shape(self):
        create_vector_const(self.context, OpTypeFloat, size=4)
        create_vector_const(self.context, OpTypeFloat, size=2)

        outer_product: OpOuterProduct = OpOuterProduct().fuzz(self.context)[-1]

        # columns
        self.assertEqual(len(outer_product.type), len(outer_product.operand2.type))
        # rows
        self.assertEqual(len(outer_product.type.type), len(outer_product.operand1.type))

    def test_vector_times_matrix_has_correct_shape(self):
        create_vector_const(self.context, OpTypeFloat, size=4)
        create_vector_const(self.context, OpTypeFloat, size=2)

        # Here we get either: mat2x2, mat2x4, mat4x2, mat4x4
        outer_product: OpOuterProduct = OpOuterProduct().fuzz(self.context)[-1]
        self.context.symbol_table[outer_product] = outer_product.id

        # This should always find operands
        vector_times_matrix: OpVectorTimesMatrix = OpVectorTimesMatrix().fuzz(
            self.context
        )[-1]

        # The resulting vector must have as many elements as the matrix has columns
        self.assertEqual(len(vector_times_matrix.type), len(outer_product.type.type))

    def test_matrix_times_vector_has_correct_shape(self):
        create_vector_const(self.context, OpTypeFloat, size=4)
        create_vector_const(self.context, OpTypeFloat, size=2)

        # Here we get either: mat2x2, mat2x4, mat4x2, mat4x4
        outer_product: OpOuterProduct = OpOuterProduct().fuzz(self.context)[-1]
        self.context.symbol_table[outer_product] = outer_product.id

        # This should always find operands
        matrix_times_vector: OpMatrixTimesVector = OpMatrixTimesVector().fuzz(
            self.context
        )[-1]

        # The resulting vector must have as many elements as the matrix has rows
        self.assertEqual(len(matrix_times_vector.type), len(outer_product.type.type))

    def test_matrix_times_matrix_has_correct_shape(self):
        create_vector_const(self.context, OpTypeFloat, size=4)
        create_vector_const(self.context, OpTypeFloat, size=2)

        # Here we get either: mat2x2, mat2x4, mat4x2, mat4x4
        outer_product1: OpOuterProduct = OpOuterProduct().fuzz(self.context)[-1]
        self.context.symbol_table[outer_product1] = outer_product1.id

        # We do this to avoid having two outer products that
        # eeturn a mat2x4/mat4x2 which will fail the test
        outer_product2 = copy.deepcopy(outer_product1)
        while outer_product2 == outer_product1:
            outer_product2: OpOuterProduct = OpOuterProduct().fuzz(self.context)[-1]
        self.context.symbol_table[outer_product2] = outer_product2.id

        # This should always find operands
        matrix_times_matrix: OpMatrixTimesMatrix = OpMatrixTimesMatrix().fuzz(
            self.context
        )[-1]

        # The resulting matrix must have as many rows as the first operand
        self.assertEqual(
            len(matrix_times_matrix.type.type),
            len(matrix_times_matrix.operand1.type.type),
        )
        # The resulting matrix must have as many columns as the second operand
        self.assertEqual(
            len(matrix_times_matrix.type.type), len(matrix_times_matrix.operand2.type)
        )
