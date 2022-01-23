import random
from dataclasses import dataclass, field
from typing import Dict, List, Sequence
from uuid import uuid4

from langspec.enums import (AddressingModel, Capability, ExecutionMode,
                            ExecutionModel, MemoryModel)
from langspec.opcodes import OpCode
from langspec.opcodes.context import Context
from langspec.opcodes.memory import OpVariable
from langspec.opcodes.misc import (OpCapability, OpEntryPoint, OpExecutionMode,
                                   OpMemoryModel)


@dataclass
class Shader:
    generation_path: List[str]


@dataclass
class GLSLShader(Shader):
    pass


@dataclass
class HLSLShader(Shader):
    pass


def id_generator(i=1):
    while True:
        yield i
        i += 1


@dataclass
class SPIRVShader(Shader):
    capabilities: List[OpCapability]
    # extension: Optional[List[Extension]]
    # ext_inst: List[ExtInstImport]
    memory_model: OpMemoryModel
    entry_point: OpEntryPoint
    execution_mode: OpExecutionMode
    opcodes: List[OpCode]
    context: Context

    @classmethod
    def gen(cls) -> "SPIRVShader":
        context = Context.create_global_context()
        # Generate random types and constants to be used by the program
        context.gen_types()
        context.gen_constants()
        context.gen_variables()

        # Populate function bodies
        program: List[OpCode] = context.gen_program()

        # Remap IDs
        id_gen = id_generator()
        for tvc in context.tvc.keys():
            tvc.id = next(id_gen)
            context.tvc[tvc] = tvc.id
        for opcode in program:
            opcode.id = next(id_gen)

        interfaces: Sequence[OpVariable] = context.get_interfaces()
        entry_point = OpEntryPoint(
            execution_model=ExecutionModel.GLCompute,
            function=context.main_fn,
            name="main",
            interfaces=interfaces,
        )
        capabilities = [OpCapability(capability=Capability.Shader)]
        memory_model = OpMemoryModel(
            addressing_model=AddressingModel.Logical, memory_model=MemoryModel.GLSL450
        )
        execution_mode = OpExecutionMode(
            function=entry_point, execution_mode=ExecutionMode.LocalSize
        )
        return cls(
            [cls],
            capabilities,
            memory_model,
            entry_point,
            execution_mode,
            program,
            context,
        )

    def to_file(self):
        # Generate assembly
        spasm = []
        with open("out.spasm", "w") as f:
            for capability in self.capabilities:
                f.write(capability.to_spasm(self.context))
                f.write("\n")
            f.write(self.memory_model.to_spasm(self.context))
            f.write("\n")
            f.write(self.entry_point.to_spasm(self.context))
            f.write("\n")
            # f.write(self.execution_mode.to_spasm(self.TVC_table))
            # f.write("\n")
            for tvc, _ in self.context.tvc.items():
                f.write(tvc.to_spasm(self.context))
                f.write("\n")
            for opcode in self.opcodes:
                f.write(opcode.to_spasm(self.context))
                f.write("\n")


# opcodes = [void_type, main_type, main]

# current_instruction = main
# i = 0
# opcodes += current_instruction.fuzz(id_gen=id_gen)
# current_instruction = opcodes[-1]
# spv_program = list(map(lambda opcode: opcode.to_spasm(), opcodes))
# print(spv_program)

# void main()
# {
#     vec4 scale = vec4(1.0, 1.0, 2.0, 1.0);

#     if (cond)
#         color = color1 + 1
#     else
#         color = sqrt(color2) * scale;

#     for (int i = 0; i < 4; ++i)
#         color *= multiplier;
# }

SPIRVShader.gen()

# vec = OpTypeVector()
# vec.fuzz({})
# print(vec.to_spasm({}))
