import copy
import unittest
from tempfile import NamedTemporaryFile

from omegaconf import OmegaConf

from run import SPIRVSmithConfig
from src import FuzzDelegator
from src.context import Context
from src.enums import ExecutionModel
from src.fuzzing_server import ShaderGenerator
from src.monitor import Monitor
from src.shader_parser import parse_spirv_assembly_file
from src.shader_utils import SPIRVShader

config = OmegaConf.structured(SPIRVSmithConfig())
init_strategy = copy.deepcopy(config.strategy)
init_limits = copy.deepcopy(config.limits)

config.misc.broadcast_generated_shaders = False
config.misc.start_web_server = False
config.misc.upload_logs = False
monitor = Monitor(config)


class TestParser(unittest.TestCase):
    def setUp(self):
        FuzzDelegator.reset_parametrizations()
        config.limits = copy.deepcopy(init_limits)
        config.strategy = copy.deepcopy(init_strategy)
        self.context: Context = Context.create_global_context(
            ExecutionModel.GLCompute, config
        )

    def test_parser_fully_reconstructs_tvc(self):
        shader: SPIRVShader = ShaderGenerator(config, None).gen_shader()
        with NamedTemporaryFile(suffix=".spasm") as tmp:
            shader.generate_assembly_file(tmp.name)
            parsed_shader: SPIRVShader = parse_spirv_assembly_file(tmp.name)
            self.assertSetEqual(
                set(shader.context.tvc.keys()), set(parsed_shader.context.tvc.keys())
            )

    def test_parser_fully_reconstructs_operands(self):
        shader: SPIRVShader = ShaderGenerator(config, None).gen_shader()
        with NamedTemporaryFile(suffix=".spasm") as tmp:
            shader.generate_assembly_file(tmp.name)
            parsed_shader: SPIRVShader = parse_spirv_assembly_file(tmp.name)
            self.assertListEqual(shader.opcodes, parsed_shader.opcodes)

    def test_parser_fully_reconstructs_annotatons(self):
        shader: SPIRVShader = ShaderGenerator(config, None).gen_shader()
        with NamedTemporaryFile(suffix=".spasm") as tmp:
            shader.generate_assembly_file(tmp.name)
            parsed_shader: SPIRVShader = parse_spirv_assembly_file(tmp.name)
            self.assertSetEqual(
                set(shader.context.annotations.keys()),
                set(parsed_shader.context.annotations.keys()),
            )

    def test_parser_reconstructs_entry_point(self):
        shader: SPIRVShader = ShaderGenerator(config, None).gen_shader()
        with NamedTemporaryFile(suffix=".spasm") as tmp:
            shader.generate_assembly_file(tmp.name)
            parsed_shader: SPIRVShader = parse_spirv_assembly_file(tmp.name)
            self.assertEqual(shader.entry_point, parsed_shader.entry_point)

    def test_parser_reconstructs_execution_mode(self):
        shader: SPIRVShader = ShaderGenerator(config, None).gen_shader()
        with NamedTemporaryFile(suffix=".spasm") as tmp:
            shader.generate_assembly_file(tmp.name)
            parsed_shader: SPIRVShader = parse_spirv_assembly_file(tmp.name)
            self.assertEqual(shader.execution_mode, parsed_shader.execution_mode)

    def test_parser_reconstructs_memory_model(self):
        shader: SPIRVShader = ShaderGenerator(config, None).gen_shader()
        with NamedTemporaryFile(suffix=".spasm") as tmp:
            shader.generate_assembly_file(tmp.name)
            parsed_shader: SPIRVShader = parse_spirv_assembly_file(tmp.name)
            self.assertEqual(shader.memory_model, parsed_shader.memory_model)

    def test_parser_reconstructs_capabilities(self):
        shader: SPIRVShader = ShaderGenerator(config, None).gen_shader()
        with NamedTemporaryFile(suffix=".spasm") as tmp:
            shader.generate_assembly_file(tmp.name)
            parsed_shader: SPIRVShader = parse_spirv_assembly_file(tmp.name)
            self.assertListEqual(shader.capabilities, parsed_shader.capabilities)

    def test_parsed_shader_generates_same_assembly_file(self):
        shader: SPIRVShader = ShaderGenerator(config, None).gen_shader()
        with NamedTemporaryFile(suffix=".spasm") as orig_tmp:
            shader.generate_assembly_file(orig_tmp.name)
            parsed_shader: SPIRVShader = parse_spirv_assembly_file(orig_tmp.name)
            with NamedTemporaryFile(suffix=".spasm") as parsed_tmp:
                parsed_shader.generate_assembly_file(parsed_tmp.name)
                with open(orig_tmp.name, "r") as orig_file:
                    with open(parsed_tmp.name, "r") as parsed_file:
                        original_lines = list(map(str.strip, orig_file.readlines()))
                        parsed_lines = list(map(str.strip, parsed_file.readlines()))
                        self.assertListEqual(original_lines, parsed_lines)
