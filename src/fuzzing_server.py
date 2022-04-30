import logging
import os
import subprocess
from dataclasses import dataclass
from dataclasses import field
from threading import Thread
from typing import Sequence
from typing import TYPE_CHECKING

import firebase_admin
import ulid
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud import storage
from omegaconf import OmegaConf
from shortuuid import uuid
from ulid import ULID

from src import FuzzDelegator
from src import OpCode
from src.amber_generator import AmberGenerator
from src.context import Context
from src.enums import AddressingModel
from src.enums import Capability
from src.enums import ExecutionMode
from src.enums import ExecutionModel
from src.enums import MemoryModel
from src.enums import StorageClass
from src.extension import OpExtInstImport
from src.misc import OpCapability
from src.misc import OpEntryPoint
from src.misc import OpExecutionMode
from src.misc import OpMemoryModel
from src.monitor import Event
from src.monitor import Monitor
from src.operators.memory.memory_access import OpVariable
from src.recondition import recondition

if TYPE_CHECKING:
    from run import SPIRVSmithConfig

from google.cloud import bigquery

import signal
from flask import Flask

app = Flask(__name__)

logging.getLogger("werkzeug").disabled = True


def get_BQ_client() -> bigquery.Client:
    return bigquery.Client.from_service_account_json("infra/spirvsmith_gcp.json")


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
    capabilities: list[OpCapability]
    # extension: Optional[list[Extension]]
    # ext_inst: list[ExtInstImport]
    memory_model: OpMemoryModel
    entry_point: OpEntryPoint
    execution_mode: OpExecutionMode
    opcodes: list[OpCode]
    context: Context

    def export(self):
        # Generate assembly
        self.id = uuid()
        os.mkdir(f"out/{self.id}")
        self.filename = f"out/{self.id}/shader.spasm"
        with open(self.filename, "w") as f:
            f.write("; Magic:     0x07230203 (SPIR-V)\n")
            f.write("; Version:   0x00010300 (Version: 1.3.0)\n")
            f.write("; Generator: 0x00220001 (SPIRVSmith)\n")
            f.write(f"; Bound:     {len(self.opcodes) + len(self.context.tvc) - 1}\n")
            f.write("; Schema:    0\n")
            for capability in self.capabilities:
                f.write(capability.to_spasm(self.context))
                f.write("\n")
            for ext in self.context.extension_sets.values():
                f.write(ext.to_spasm(self.context))
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
            for annotation in self.context.annotations:
                f.write(annotation.to_spasm(self.context))
                f.write("\n")
            for tvc, _ in self.context.tvc.items():
                if (
                    isinstance(tvc, OpVariable)
                    and tvc.storage_class == StorageClass.Function
                ):
                    continue
                f.write(tvc.to_spasm(self.context))
                f.write("\n")
            for opcode in self.opcodes:
                f.write(opcode.to_spasm(self.context))
                f.write("\n")


def id_generator(i=1):
    while True:
        yield i
        i += 1


def create_GCS_folder(bucket: storage.Bucket, folder_name: str):
    blob = bucket.blob(folder_name)
    blob.upload_from_string("")


def upload_local_file_to_GCS(
    bucket: storage.Bucket, local_filename: str, destination_filename: str
):
    blob = bucket.blob(destination_filename)
    blob.upload_from_filename(local_filename)


def broadcast_shader_data(generator_id: ULID, shader: SPIRVShader, monitor: Monitor):
    bucket = storage.Client.from_service_account_json(
        "infra/spirvsmith_gcp.json"
    ).get_bucket("spirv_shaders_bucket")
    create_GCS_folder(bucket, shader.id)
    upload_local_file_to_GCS(
        bucket, f"out/{shader.id}/shader.spasm", f"{shader.id}/shader.spasm"
    )
    upload_local_file_to_GCS(
        bucket, f"out/{shader.id}/out.amber", f"{shader.id}/out.amber"
    )
    upload_local_file_to_GCS(
        bucket, f"out/{shader.id}/shader.spv", f"{shader.id}/shader.spv"
    )
    monitor.info(event=Event.GCS_UPLOAD_SUCCESS, extra={"shader_id": shader.id})
    BQ_client = get_BQ_client()
    errors = BQ_client.insert_rows_json(
        "spirvsmith.spirv.shader_data",
        [
            {
                "shader_id": shader.id,
                "n_buffers": len(shader.context.get_storage_buffers()),
                "generator_id": str(generator_id),
                "generator_version": shader.context.config.misc.version,
                "buffer_dump": None,
                "platform_os": None,
                "platform_hardware_type": None,
                "platform_hardware_vendor": None,
                "platform_hardware_model": None,
                "platform_backend": None,
            }
        ],
    )
    if errors == []:
        monitor.info(
            event=Event.BQ_SHADER_DATA_UPSERT_SUCCESS,
            extra={"shader_id": shader.id, "generator_id": str(generator_id)},
        )
    else:
        monitor.error(
            event=Event.BQ_SHADER_DATA_UPSERT_FAILURE,
            extra={
                "errors": errors,
                "shader_id": shader.id,
                "generator_id": str(generator_id),
            },
        )


@dataclass
class ShaderGenerator:
    config: "SPIRVSmithConfig"
    monitor: Monitor = field(default_factory=Monitor)
    amber_generator: AmberGenerator = field(default_factory=AmberGenerator)
    generator_id: ULID = field(default_factory=ulid.new)

    def start(self):
        if self.config.misc.start_web_server:
            flask_thread = ServerThread(app)
            flask_thread.start()

        if self.config.misc.broadcast_generated_shaders:
            cred = credentials.Certificate("infra/spirvsmith_gcp.json")
            firebase_admin.initialize_app(cred)

            firestore_client = firestore.client()
            document_reference = firestore_client.collection("configurations").document(
                str(self.generator_id)
            )
            document_reference.set(OmegaConf.to_container(self.config))

        self.amber_generator.config = self.config
        self.amber_generator.monitor = self.monitor

        try:
            os.mkdir("out")
        except FileExistsError:
            pass
        while True:
            if terminate:
                self.monitor.info(event=Event.TERMINATED)
                if self.config.misc.start_web_server:
                    flask_thread.shutdown()
                    flask_thread.join()
                break
            if not paused:
                shader = self.gen_shader()
                shader.export()

                if (
                    self.assemble(shader)
                    and self.validate(shader)
                    and self.gen_optimised(shader)
                    and self.validate(shader, opt=True)
                ):
                    self.amber_generator.submit(shader)
                    if self.config.misc.broadcast_generated_shaders:
                        Thread(
                            target=broadcast_shader_data,
                            args=(self.generator_id, shader, self.monitor),
                        ).start()
                if paused:
                    self.monitor.info(event=Event.PAUSED)

    def assemble(self, shader: SPIRVShader):
        process: subprocess.CompletedProcess = subprocess.run(
            [
                self.config.binaries.ASSEMBLER_PATH,
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
                self.config.binaries.OPTIMISER_PATH,
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
                self.config.binaries.VALIDATOR_PATH,
                "--target-env",
                "vulkan1.2",
                f"out/{shader.id}/{'spv_opt/' if opt else ''}shader.spv",
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
        # execution_model = random.SystemRandom().choice(list(ExecutionModel))
        # execution_model = random.SystemRandom().choice(
        #     [ExecutionModel.GLCompute, ExecutionModel.Kernel]
        # )
        execution_model = ExecutionModel.GLCompute
        context = Context.create_global_context(
            execution_model, self.config, self.monitor
        )
        if self.config.strategy.enable_ext_glsl_std_450:
            context.extension_sets["GLSL"] = OpExtInstImport(name="GLSL.std.450")
        # Generate random types and constants to be used by the program
        context.gen_types()
        context.gen_constants()
        context.gen_global_variables()

        # Populate function bodies and recondition
        program: list[OpCode] = context.gen_program()
        program: list[OpCode] = recondition(context, program)
        FuzzDelegator.reset_parametrizations()

        # Remap IDs
        id_gen = id_generator()
        for ext in context.extension_sets.values():
            ext.id = next(id_gen)
        new_tvc = {}
        for tvc in context.tvc.keys():
            tvc.id = next(id_gen)
            new_tvc[tvc] = tvc.id
        context.tvc = new_tvc
        for opcode in program:
            opcode.id = next(id_gen)

        interfaces: Sequence[OpVariable] = context.get_interfaces()
        entry_point = OpEntryPoint(
            execution_model=execution_model,
            function=context.main_fn,
            name="main",
            interfaces=interfaces,
        )
        capabilities = [
            OpCapability(capability=Capability.Shader),
            OpCapability(capability=Capability.Matrix),
            # OpCapability(capability=Capability.Vector16),
        ]
        memory_model = OpMemoryModel(
            addressing_model=AddressingModel.Logical, memory_model=MemoryModel.GLSL450
        )
        # TODO extra operands
        if execution_model == ExecutionModel.GLCompute:
            execution_mode = ExecutionMode.LocalSize
        else:
            execution_mode = ExecutionMode.OriginUpperLeft
        op_execution_mode = OpExecutionMode(entry_point.function, execution_mode)
        return SPIRVShader(
            [self],
            capabilities,
            memory_model,
            entry_point,
            op_execution_mode,
            program,
            context,
        )
