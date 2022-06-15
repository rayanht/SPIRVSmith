import copy
import multiprocessing
import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from multiprocessing.pool import Pool
from typing import Optional
from typing import TYPE_CHECKING

import tqdm
from spirv_enums import AddressingModel
from spirv_enums import Capability
from spirv_enums import ExecutionMode
from spirv_enums import ExecutionModel
from spirv_enums import MemoryModel
from spirvsmith_server_client.api.generators import register_generator
from spirvsmith_server_client.api.shaders import submit_shader
from spirvsmith_server_client.models import *

from src import FuzzDelegator
from src import OpCode
from src.context import Context
from src.extension import OpExtInstImport
from src.misc import OpCapability
from src.misc import OpEntryPoint
from src.misc import OpExecutionMode
from src.misc import OpMemoryModel
from src.monitor import Event
from src.monitor import Monitor
from src.operators.memory.memory_access import OpVariable
from src.optimiser_fuzzer import fuzz_optimiser
from src.shader_utils import SPIRVShader
from src.types.concrete_types import OpTypeFunction
from src.types.concrete_types import OpTypeVoid

if TYPE_CHECKING:
    from run import SPIRVSmithConfig

import signal

from spirvsmith_server_client import Client

client = Client(base_url="http://spirvsmith.hatout.dev")


terminate = False
paused = False


def signal_handling(signum, frame):
    global terminate
    terminate = True


signal.signal(signal.SIGINT, signal_handling)


def init_MP_pool():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


@dataclass
class ShaderGenerator:
    config: "SPIRVSmithConfig"
    generator_info: Optional[GeneratorInfo] = None

    def start(self):
        MP_pool: Pool = multiprocessing.Pool(4, init_MP_pool)
        thread_pool_executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=4)

        if self.config.misc.broadcast_generated_shaders:
            register_generator.sync(client=client, json_body=self.generator_info)
        os.makedirs(self.config.misc.out_folder, exist_ok=True)
        max_shaders: int = (
            self.config.limits.max_shaders if self.config.limits.max_shaders else 1000
        )
        print(f"SPIRVSmith will generate {max_shaders} shaders...")
        print(f"Selected Generation Policy: {self.config.strategy.gp_policy}")
        print(f"Selected Recency Bias Policy: {self.config.strategy.rbp_policy}")
        for _ in range(max_shaders):
            if terminate:
                MP_pool.close()
                MP_pool.join()
                thread_pool_executor.shutdown()
                Monitor(self.config).info(event=Event.TERMINATED)
                break
            if not paused:
                shader: SPIRVShader = self.gen_shader()
                shader.generate_assembly_file(
                    f"{self.config.misc.out_folder}/{shader.id}.spasm"
                )
                if shader.validate():
                    if self.config.misc.fuzz_optimiser:
                        MP_pool.apply_async(func=fuzz_optimiser, args=(shader,))
                    if self.config.misc.broadcast_generated_shaders:
                        submit_shader.sync(
                            client=client,
                            json_body=ShaderSubmission(
                                shader_id=shader.id,
                                shader_assembly="\n".join(
                                    shader.generate_assembly_lines()
                                ),
                                generator_info=self.generator_info,
                                prioritize=False,
                                n_buffers=len(shader.context.get_storage_buffers()),
                            ),
                        )

            if paused:
                Monitor(self.config).info(event=Event.PAUSED)

    def gen_shader(self) -> SPIRVShader:
        execution_model = ExecutionModel.GLCompute
        context: Context = Context.create_global_context(execution_model, self.config)
        void_type: OpTypeVoid = OpTypeVoid()
        main_type: OpTypeFunction = OpTypeFunction(
            return_type=void_type, parameter_types=()
        )
        context.main_type = main_type
        context.globals[void_type] = void_type.id
        context.globals[main_type] = main_type.id
        # context.extension_sets["SPV_KHR_bit_instructions"] = OpExtension(
        #     "SPV_KHR_bit_instructions"
        # )
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
        entry_point: OpEntryPoint = OpEntryPoint(
            execution_model=execution_model,
            function=context.main_fn,
            name="main",
            interfaces=interfaces,
        )
        capabilities: list[OpCapability] = [
            OpCapability(capability=Capability.Shader),
            OpCapability(capability=Capability.Matrix),
            # OpCapability(capability=Capability.BitInstructions),
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
