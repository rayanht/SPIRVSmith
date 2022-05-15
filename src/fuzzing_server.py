import copy
import logging
import multiprocessing
import os
import random
import tempfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from dataclasses import field
from threading import Thread
from typing import TYPE_CHECKING
from uuid import uuid4

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from omegaconf import OmegaConf

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
from src.shader_brokerage import BQ_insert_new_shader
from src.shader_brokerage import GCS_upload_shader
from src.shader_utils import SPIRVShader
from src.types.concrete_types import OpTypeFunction
from src.types.concrete_types import OpTypeVoid
from src.utils import mutate_config

if TYPE_CHECKING:
    from run import SPIRVSmithConfig


import signal
from flask import Flask

app = Flask(__name__)

logging.getLogger("werkzeug").disabled = True


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


def register_generator_configuration(generator_id: str, config: "SPIRVSmithConfig"):
    firestore_client = firestore.client()
    document_reference = firestore_client.collection("configurations").document(
        str(generator_id)
    )
    document_reference.set(OmegaConf.to_container(config))


@dataclass
class ShaderGenerator:
    config: "SPIRVSmithConfig"
    generator_id: str = field(default_factory=lambda: str(uuid4()))

    def start(self):
        MP_pool = multiprocessing.Pool(4, init_MP_pool)
        thread_pool_executor = ThreadPoolExecutor(max_workers=4)
        if self.config.misc.start_web_server:
            flask_thread = ServerThread(app)
            flask_thread.start()

        if self.config.misc.broadcast_generated_shaders:
            cred = credentials.Certificate("infra/spirvsmith_gcp.json")
            firebase_admin.initialize_app(cred)
            register_generator_configuration(self.generator_id, self.config)

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
                Monitor(self.config).info(event=Event.TERMINATED)
                break
            if not paused:
                shader: SPIRVShader = self.gen_shader()
                shader.generate_assembly_file(f"out/{shader.id}.spasm")
                if shader.validate():
                    MP_pool.apply_async(func=fuzz_optimiser, args=(shader,))
                    if self.config.misc.broadcast_generated_shaders:
                        thread_pool_executor.submit(GCS_upload_shader, shader)
                        thread_pool_executor.submit(
                            BQ_insert_new_shader, shader, self.generator_id
                        )
            if paused:
                Monitor(self.config).info(event=Event.PAUSED)

            if random.SystemRandom().random() <= self.config.strategy.mutation_rate:
                old_strategy = copy.deepcopy(self.config.strategy)
                mutate_config(self.config)
                self.generator_id = str(uuid4())
                if self.config.misc.broadcast_generated_shaders:
                    register_generator_configuration(self.generator_id, self.config)
                Monitor(self.config).info(
                    event=Event.GENERATOR_MUTATION,
                    extra={
                        "old_strategy": old_strategy,
                        "new_strategy": self.config.strategy,
                    },
                )

    def gen_shader(self) -> SPIRVShader:
        # execution_model = random.SystemRandom().choice(list(ExecutionModel))
        # execution_model = random.SystemRandom().choice(
        #     [ExecutionModel.GLCompute, ExecutionModel.Kernel]
        # )
        execution_model = ExecutionModel.GLCompute
        context: Context = Context.create_global_context(execution_model, self.config)
        void_type: OpTypeVoid = OpTypeVoid()
        main_type: OpTypeFunction = OpTypeFunction(
            return_type=void_type, parameter_types=()
        )
        context.main_type = main_type
        context.tvc[void_type] = void_type.id
        context.tvc[main_type] = main_type.id

        if self.config.strategy.enable_ext_glsl_std_450:
            context.extension_sets["GLSL.std.450"] = OpExtInstImport(
                name="GLSL.std.450"
            )
        # Generate random types and constants to be used by the program
        context.gen_types()
        context.gen_constants()
        context.gen_global_variables()

        # Populate function bodies
        opcodes: list[OpCode] = context.gen_opcodes()

        interfaces: tuple[OpVariable, ...] = context.get_interfaces()
        entry_point = OpEntryPoint(
            execution_model=execution_model,
            function=context.main_fn,
            name="main",
            interfaces=interfaces,
        )
        capabilities: list[OpCapability] = [
            OpCapability(capability=Capability.Shader),
            OpCapability(capability=Capability.Matrix),
        ]
        memory_model: OpMemoryModel = OpMemoryModel(
            addressing_model=AddressingModel.Logical, memory_model=MemoryModel.GLSL450
        )

        if execution_model == ExecutionModel.GLCompute:
            op_execution_mode: OpExecutionMode = OpExecutionMode(
                entry_point.function, ExecutionMode.LocalSize, (1, 1, 1)
            )
        else:
            op_execution_mode: OpExecutionMode = OpExecutionMode(
                entry_point.function, ExecutionMode.OriginUpperLeft
            )

        shader: SPIRVShader = SPIRVShader(
            capabilities,
            memory_model,
            entry_point,
            op_execution_mode,
            opcodes,
            context,
        )

        shader: SPIRVShader = shader.recondition().normalise_ids()

        FuzzDelegator.reset_parametrizations()

        return shader
