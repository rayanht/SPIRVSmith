import logging
import multiprocessing
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from dataclasses import field
from threading import Thread
from typing import Sequence
from typing import TYPE_CHECKING

import firebase_admin
import ulid
from firebase_admin import credentials
from firebase_admin import firestore
from omegaconf import OmegaConf
from ulid import ULID

from src import FuzzDelegator
from src import OpCode
from src.context import Context
from src.enums import AddressingModel
from src.enums import Capability
from src.enums import ExecutionMode
from src.enums import ExecutionModel
from src.enums import MemoryModel
from src.extension import OpExtInstImport
from src.misc import OpCapability
from src.misc import OpEntryPoint
from src.misc import OpExecutionMode
from src.misc import OpMemoryModel
from src.monitor import Event
from src.monitor import Monitor
from src.operators.memory.memory_access import OpVariable
from src.optimiser_fuzzer import fuzz_optimiser
from src.recondition import recondition
from src.shader_brokerage import insert_new_shader_into_BQ
from src.shader_brokerage import upload_shader_to_gcs
from src.shader_utils import assemble_shader
from src.shader_utils import SPIRVShader
from src.shader_utils import validate_spirv_file

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


def init_MP_pool():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


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


def id_generator(i=1):
    while True:
        yield i
        i += 1


@dataclass
class ShaderGenerator:
    config: "SPIRVSmithConfig"
    generator_id: ULID = field(default_factory=ulid.new)

    def start(self):
        MP_pool = multiprocessing.Pool(4, init_MP_pool)
        thread_pool_executor = ThreadPoolExecutor(max_workers=4)
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

        try:
            os.mkdir("out")
        except FileExistsError:
            pass
        while True:
            if terminate:
                if self.config.misc.start_web_server:
                    flask_thread.shutdown()
                    flask_thread.join()
                MP_pool.close()
                MP_pool.join()
                thread_pool_executor.shutdown()
                Monitor().info(event=Event.TERMINATED)
                break
            if not paused:
                shader: SPIRVShader = self.gen_shader()

                with tempfile.NamedTemporaryFile() as tmp:
                    if assemble_shader(shader, tmp.name) and validate_spirv_file(
                        shader, tmp.name
                    ):
                        MP_pool.apply_async(func=fuzz_optimiser, args=(shader,))
                        if self.config.misc.broadcast_generated_shaders:
                            thread_pool_executor.submit(upload_shader_to_gcs, shader)
                            thread_pool_executor.submit(
                                insert_new_shader_into_BQ, shader, self.generator_id
                            )
                if paused:
                    Monitor().info(event=Event.PAUSED)

    def gen_shader(self) -> SPIRVShader:
        # execution_model = random.SystemRandom().choice(list(ExecutionModel))
        # execution_model = random.SystemRandom().choice(
        #     [ExecutionModel.GLCompute, ExecutionModel.Kernel]
        # )
        execution_model = ExecutionModel.GLCompute
        context = Context.create_global_context(execution_model, self.config)
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
            capabilities,
            memory_model,
            entry_point,
            op_execution_mode,
            program,
            context,
        )
