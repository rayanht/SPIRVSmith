import copy
import re
from typing import List, Optional
from paprika import data, to_string

from langspec import Capability, ExecutionMode, MemoryModel


@data
class Shader:
    generation_path: List[str]

@data
class SPIRVShader(Shader):
    capabilities: List[Capability]
    extension: Optional[List[Extension]]
    ext_inst: List[ExtInstImport]
    memory_model: MemoryModel
    entry_point: List[EntryPoint]
    execution_mode: List[ExecutionMode]
    
    function_declarations: List[FunctionDeclaration]
    function_definitions: List[FunctionDefinition]



@to_string
class GLSLShader(Shader):
    pass

@to_string
class HLSLShader(Shader):
    pass


class SPIRVFuzzer:
    def generate(self) -> SPIRVShader:
        shader = SPIRVShader()
        shader.generation_path = []
        shader.generation_path.append(self.__class__)
        return shader


class GLSLCrossCompiler:
    def compile(self, in_shader: Shader) -> GLSLShader:
        out_shader = copy.deepcopy(in_shader)
        out_shader.generation_path.append(self.__class__)
        return out_shader


class HLSLCrossCompiler:

    def compile(self, in_shader: Shader) -> HLSLShader:
        out_shader = copy.deepcopy(in_shader)
        out_shader.generation_path.append(self.__class__)
        return out_shader


class AmberscriptGenerator:
    pass


fuzzer = SPIRVFuzzer()
glsl_cross_compiler = GLSLCrossCompiler()
hlsl_cross_compiler = HLSLCrossCompiler()
amberscript_generator = AmberscriptGenerator()

spirv_shaders: List[SPIRVShader] = [fuzzer.generate() for _ in range(5)]
glsl_shaders: List[GLSLShader] = [glsl_cross_compiler.compile(shader) for shader in spirv_shaders]
hlsl_shaders: List[HLSLShader] = [hlsl_cross_compiler.compile(shader) for shader in spirv_shaders]

