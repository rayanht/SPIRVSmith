from aifc import Error
from dataclasses import dataclass, field
from enum import Enum
import os
import random
from typing import TYPE_CHECKING, List, Sequence

from monitor import Event, Monitor
from src.types.concrete_types import OpTypeFloat, OpTypeInt
from shortuuid import uuid
from src.enums import (
    AddressingModel,
    Capability,
    ExecutionMode,
    ExecutionModel,
    MemoryModel,
)
import subprocess
from src import OpCode
from src.context import Context
from src.memory import OpVariable
from src.misc import (
    OpCapability,
    OpEntryPoint,
    OpExecutionMode,
    OpMemoryModel,
)

if TYPE_CHECKING:
    from run import SPIRVSmithConfig


import signal, sys, time

terminate = False


def signal_handling(signum, frame):
    global terminate
    terminate = True


signal.signal(signal.SIGINT, signal_handling)


@dataclass
class Shader:
    id: str


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

    def export(self):
        # Generate assembly
        self.id = uuid()
        os.mkdir(f"out/{self.id}")
        self.filename = f"out/{self.id}/shader.spasm"
        with open(self.filename, "w") as f:
            for capability in self.capabilities:
                f.write(capability.to_spasm(self.context))
                f.write("\n")
            f.write(self.memory_model.to_spasm(self.context))
            f.write("\n")
            f.write(self.entry_point.to_spasm(self.context))
            f.write("\n")
            # TODO
            # f.write(self.execution_mode.to_spasm(self.context))
            # f.write("\n")
            f.write(
                f"OpExecutionMode %{self.execution_mode.function.id} {self.execution_mode.execution_mode} 1 1 1"
            )
            f.write("\n")
            for tvc, _ in self.context.tvc.items():
                f.write(tvc.to_spasm(self.context))
                f.write("\n")
            for opcode in self.opcodes:
                f.write(opcode.to_spasm(self.context))
                f.write("\n")


def id_generator(i=1):
    while True:
        yield i
        i += 1


@dataclass
class ShaderGenerator:
    config: "SPIRVSmithConfig"
    monitor: Monitor = field(default_factory=Monitor)

    def start(self):
        try:
            os.mkdir("out")
        except FileExistsError:
            pass
        while not terminate:
            shader = self.gen_shader()
            shader.export()

            # Without spirv-opt
            if not self.assemble(shader):
                continue
            if not self.validate(shader):
                continue

            # With spirv-opt
            if self.gen_optimised(shader):
                self.validate(shader, opt=True)

            if self.gen_amber(shader):
                self.run_amber(shader)

            if terminate:
                self.monitor.info(event=Event.TERMINATED)

    def assemble(self, shader: SPIRVShader):
        process: subprocess.CompletedProcess = subprocess.run(
            [
                self.config.ASSEMBLER_PATH,
                "--target-env",
                "spv1.3",
                f"out/{shader.id}/shader.spasm",
                "-o",
                f"out/{shader.id}/shader.spv",
            ],
            capture_output=True,
        )
        if process.returncode != 0:
            self.monitor.error(
                event=Event.ASSEMBLER_FAILURE,
                extra={
                    "stderr": process.stderr.decode("utf-8"),
                    "cli_args": str(process.args),
                    "shader_id": shader.id,
                },
            )
        else:
            self.monitor.info(
                event=Event.ASSEMBLER_SUCCESS, extra={"shader_id": shader.id}
            )

        return process.returncode == 0

    def gen_optimised(self, shader: SPIRVShader):
        os.mkdir(f"out/{shader.id}/spv_opt")
        process: subprocess.CompletedProcess = subprocess.run(
            [
                self.config.OPTIMISER_PATH,
                "--target-env=spv1.3",
                f"out/{shader.id}/shader.spv",
                "-o",
                f"out/{shader.id}/spv_opt/shader.spv",
            ],
            capture_output=True,
        )
        if process.returncode != 0:
            self.monitor.error(
                event=Event.OPTIMIZER_FAILURE,
                extra={
                    "stderr": process.stderr.decode("utf-8"),
                    "cli_args": str(process.args),
                    "shader_id": shader.id,
                },
            )
        else:
            self.monitor.info(
                event=Event.OPTIMIZER_SUCCESS, extra={"shader_id": shader.id}
            )

        return process.returncode == 0

    def validate(self, shader: SPIRVShader, opt: bool = False):
        process: subprocess.CompletedProcess = subprocess.run(
            [
                self.config.VALIDATOR_PATH,
                f"out/{shader.id}/{'spv_opt/' if opt else '/'}shader.spv",
            ],
            capture_output=True,
        )
        if process.returncode != 0:
            self.monitor.error(
                event=Event.VALIDATOR_OPT_FAILURE if opt else Event.VALIDATOR_FAILURE,
                extra={
                    "stderr": process.stderr.decode("utf-8"),
                    "cli_args": str(process.args),
                    "shader_id": shader.id,
                },
            )
        else:
            self.monitor.info(
                event=Event.VALIDATOR_OPT_SUCCESS if opt else Event.VALIDATOR_SUCCESS,
                extra={"shader_id": shader.id},
            )

        return process.returncode == 0

    def run_amber(self, shader: SPIRVShader):
        process: subprocess.CompletedProcess = subprocess.run(
            [
                self.config.AMBER_PATH,
                f"out/{shader.id}/out.amber",
            ],
            capture_output=True,
        )
        if process.returncode != 0:
            self.monitor.error(
                event=Event.AMBER_FAILURE,
                extra={
                    "stderr": process.stderr.decode("utf-8"),
                    "cli_args": str(process.args),
                    "shader_id": shader.id,
                },
            )
        else:
            self.monitor.info(event=Event.AMBER_SUCCESS, extra={"shader_id": shader.id})

        return process.returncode == 0

    def gen_amber(self, shader: SPIRVShader):
        shader_interfaces: List[OpVariable] = shader.context.get_interfaces()
        buffers: List[AmberBuffer] = []
        for k, interface in enumerate(shader_interfaces):
            match i := interface.type.type:
                case OpTypeInt() if i.signed:
                    buffers.append(
                        AmberBuffer(
                            f"buf{k}", AmberBufferType.INT32, random.randint(-64, 64)
                        )
                    )
                case OpTypeInt():
                    buffers.append(
                        AmberBuffer(
                            f"buf{k}", AmberBufferType.UINT32, random.randint(0, 128)
                        )
                    )
                case OpTypeFloat():
                    buffers.append(
                        AmberBuffer(
                            f"buf{k}", AmberBufferType.FLOAT, random.uniform(0, 128)
                        )
                    )
                case _:
                    raise Error
        with open(f"out/{shader.id}/out.amber", "w") as fw:
            fw.write("#!amber\n")
            fw.write(f"SHADER compute {'shader'} SPIRV-ASM TARGET_ENV spv1.3\n")
            with open(f"out/{shader.id}/shader.spasm", "r") as fr:
                lines = fr.readlines()
                for line in lines:
                    fw.write(line)
                fw.write("END\n")
            for buffer in buffers:
                fw.write(f"{buffer.to_amberscript()}\n")
            fw.write(f"PIPELINE {'compute'} pipeline\n")
            fw.write(f"ATTACH {'shader'}\n")
            for i, buffer in enumerate(buffers):
                fw.write(
                    f"BIND BUFFER {buffer.name} AS storage DESCRIPTOR_SET 0 BINDING {i}\n"
                )
            fw.write("END\n")
            fw.write("RUN pipeline 1 1 1\n")

    def gen_shader(self) -> SPIRVShader:
        # execution_model = random.choice(list(ExecutionModel))
        execution_model = random.choice(
            [ExecutionModel.GLCompute, ExecutionModel.Kernel]
        )
        context = Context.create_global_context(
            execution_model, self.config, self.monitor
        )
        # Generate random types and constants to be used by the program
        context.gen_types()
        context.gen_constants()
        context.gen_variables()

        # Populate function bodies
        program: List[OpCode] = context.gen_program()

        # Remap IDs
        id_gen = id_generator()
        new_tvc = {}
        for tvc in context.tvc.keys():
            tvc.id = next(id_gen)
            new_tvc[tvc] = tvc.id
        context.tvc = new_tvc
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
        # TODO extra operands
        execution_mode = OpExecutionMode(entry_point.function, ExecutionMode.LocalSize)
        return SPIRVShader(
            [self],
            capabilities,
            memory_model,
            entry_point,
            execution_mode,
            program,
            context,
        )


class AmberBufferType(Enum):
    INT8 = "int8"
    INT16 = "int16"
    INT32 = "int32"
    INT64 = "int64"
    UINT8 = "uint8"
    UINT16 = "uint16"
    UINT32 = "uint32"
    UINT64 = "uint64"
    FLOAT16 = "float16"
    FLOAT = "float"
    DOUBLE = "double"


@dataclass
class AmberBuffer:
    name: str
    type: AmberBufferType
    initializer: float | int

    def to_amberscript(self):
        return f"BUFFER {self.name} DATA_TYPE {self.type.value} STD430 DATA\n{self.initializer}\nEND"
