from typing import Optional
import unittest
from monitor import Monitor
from src.recondition import recondition
from run_local import SPIRVSmithConfig
from src import Type
from src.constants import OpConstant, OpConstantComposite
from src.context import Context
from src.enums import ExecutionModel
from src.operators.arithmetic import OpSMod
from src.operators.composite import OpVectorExtractDynamic
from src.types.concrete_types import OpTypeInt, OpTypeVector


monitor = Monitor()


def id_generator(i=1):
    while True:
        yield i
        i += 1


def create_numerical_constant_in_context(
    context: Context,
    target_type: Type,
    value: int = 0,
    width: int = 32,
    signed: Optional[int] = 0,
) -> OpTypeInt:
    type = target_type()
    type.width = width
    if signed:
        type.signed = signed
    constant = OpConstant().fuzz(context)[-1]
    constant.type = type
    constant.value = value
    context.tvc[type] = type.id
    context.tvc[constant] = constant.id
    return constant


class TestRecondition(unittest.TestCase):
    def test_vector_access_is_reconditioned(self):
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

        index = create_numerical_constant_in_context(
            context, OpTypeInt, value=5, signed=1, width=32
        )
        context.tvc[index] = index.id

        vec_constant = OpConstantComposite()
        vec_constant.type = vec_type
        vec_constant.constituents = tuple([index for _ in range(len(vec_type))])
        context.tvc[vec_type] = vec_type.id

        vec_access = OpVectorExtractDynamic()
        vec_access.type = int_type
        vec_access.vector = vec_constant
        vec_access.index = index

        opcodes = [int_type, vec_type, index, vec_constant, vec_access]

        reconditioned = recondition(context, opcodes)

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

        index = create_numerical_constant_in_context(
            context, OpTypeInt, value=5, signed=1, width=32
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
