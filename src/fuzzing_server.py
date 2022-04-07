from dataclasses import dataclass, field
from enum import Enum
from multiprocessing import Process, Value, shared_memory
import os
import random
from threading import Thread
from typing import TYPE_CHECKING, List, Sequence
from amber import AmberGenerator, AmberRunner

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
    from run_local import SPIRVSmithConfig


import signal
from flask import Flask

app = Flask(__name__)


terminate = False
paused = False

def signal_handling(signum, frame):
    global terminate
    terminate = True


signal.signal(signal.SIGINT, signal_handling)

from werkzeug.serving import make_server


class ServerThread(Thread):
    def __init__(self, app):
        Thread.__init__(self)
        self.server = make_server("127.0.0.1", 54254, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()


@app.route("/pause")
def pause_fuzzer():
    global paused
    paused = True
    return ("", 204)

@app.route("/start")
def start_fuzzer():
    global paused
    paused = False
    return ("", 204)

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
    amber_runner: AmberRunner = field(default_factory=AmberRunner)
    amber_generator: AmberGenerator = field(default_factory=AmberGenerator)

    def start(self):
        flask_thread = ServerThread(app)
        flask_thread.start()

        self.amber_runner.config = self.config
        self.amber_runner.monitor = self.monitor

        self.amber_generator.config = self.config
        self.amber_generator.monitor = self.monitor

        try:
            os.mkdir("out")
        except FileExistsError:
            pass
        while True:
            if terminate:
                self.monitor.info(event=Event.TERMINATED)
                flask_thread.shutdown()
                flask_thread.join()
                break
            if not paused:
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

                if self.amber_generator.submit(shader):
                    self.amber_runner.submit(shader)

                if paused:
                    self.monitor.info(event=Event.PAUSED)

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
