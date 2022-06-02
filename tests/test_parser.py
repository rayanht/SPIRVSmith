import copy
import unittest
from tempfile import NamedTemporaryFile

from omegaconf import OmegaConf

from run import SPIRVSmithConfig
from src import FuzzDelegator
from src.fuzzing_client import ShaderGenerator
from src.monitor import Monitor
from src.shader_parser import parse_spirv_assembly_file
from src.shader_parser import parse_spirv_assembly_lines
from src.shader_utils import SPIRVShader

config: SPIRVSmithConfig = OmegaConf.structured(SPIRVSmithConfig())
init_strategy = copy.deepcopy(config.strategy)
init_limits = copy.deepcopy(config.limits)

config.misc.broadcast_generated_shaders = False
config.misc.upload_logs = False
monitor = Monitor(config)


class TestParser(unittest.TestCase):
    def setUp(self):
        FuzzDelegator.reset_parametrizations()
        config.limits = copy.deepcopy(init_limits)
        config.strategy = copy.deepcopy(init_strategy)
        self.shader: SPIRVShader = ShaderGenerator(config, None).gen_shader()
        self.parsed_shader: SPIRVShader = parse_spirv_assembly_lines(
            self.shader.generate_assembly_lines()
        )

    def test_parser_fully_reconstructs_tvc(self):
        self.assertSetEqual(
            set(self.shader.context.globals.keys()),
            set(self.parsed_shader.context.globals.keys()),
        )

    def test_parser_fully_reconstructs_operands(self):
        self.assertListEqual(self.shader.opcodes, self.parsed_shader.opcodes)

    def test_parser_fully_reconstructs_annotatons(self):
        self.assertSetEqual(
            set(self.shader.context.annotations.keys()),
            set(self.parsed_shader.context.annotations.keys()),
        )

    def test_parser_reconstructs_entry_point(self):
        self.assertEqual(self.shader.entry_point, self.parsed_shader.entry_point)

    def test_parser_reconstructs_execution_mode(self):
        self.assertEqual(self.shader.execution_mode, self.parsed_shader.execution_mode)

    def test_parser_reconstructs_memory_model(self):
        self.assertEqual(self.shader.memory_model, self.parsed_shader.memory_model)

    def test_parser_reconstructs_capabilities(self):
        self.assertListEqual(self.shader.capabilities, self.parsed_shader.capabilities)

    def test_parsed_shader_generates_same_assembly(self):
        self.assertListEqual(
            self.shader.generate_assembly_lines(),
            self.parsed_shader.generate_assembly_lines(),
        )
