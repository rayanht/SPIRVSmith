import signal
import subprocess
import tempfile
import time
from functools import reduce
from itertools import repeat
from operator import iconcat

from dataclass_wizard import asdict
from dataclass_wizard import DumpMeta
from spirv_enums import Decoration
from vulkan_platform_py import *

from run import *
from src.annotations import OpDecorate
from src.monitor import Event
from src.monitor import Monitor
from src.shader_parser import parse_spirv_assembly_lines
from src.shader_utils import create_amber_file
from src.shader_utils import SPIRVShader
from src.utils import TARGET_SPIRV_VERSION
from src.utils import TARGET_VULKAN_VERSION

AMBER_PATH = "bin/amber"

MONITOR = Monitor()

from spirvsmith_server_client import Client

client = Client(base_url="http://localhost:8000")


terminate = False


def signal_handling(signum, frame):
    global terminate
    terminate = True


signal.signal(signal.SIGINT, signal_handling)


def run_amber(amber_filename: str, buffer_bindings: list[int], shader_id: str) -> str:
    with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
        process: subprocess.CompletedProcess = subprocess.run(
            [
                AMBER_PATH,
                "-t",
                TARGET_SPIRV_VERSION,
                "-v",
                TARGET_VULKAN_VERSION,
                "-b",
                temp_file.name,
                *reduce(
                    iconcat,
                    zip(repeat("-B"), [f"pipeline:0:{i}" for i in buffer_bindings]),
                    [],
                ),
                amber_filename,
            ],
            capture_output=True,
        )
        if process.stderr:
            MONITOR.error(
                event=Event.AMBER_FAILURE,
                extra={
                    "stderr": process.stderr.decode("utf-8"),
                    "run_args": " ".join(process.args),
                    "shader_id": shader_id,
                },
            )
            print(process.stderr.decode("utf-8"))
            return None

        if process.returncode == -signal.SIGSEGV:
            MONITOR.error(
                event=Event.AMBER_SEGFAULT,
                extra={
                    "stderr": process.stderr.decode("utf-8"),
                    "run_args": " ".join(process.args),
                    "shader_id": shader_id,
                },
            )
            print(process.stderr.decode("utf-8"))
            print("**** SEGFAULT ****")
            return "SEGFAULT"

        MONITOR.info(event=Event.AMBER_SUCCESS, extra={"shader_id": shader_id})

        with open(temp_file.name, "r") as f:
            buffer_dumps: list[str] = list(
                filter(lambda l: not l.startswith("pipeline"), f.readlines())
            )
            return " ".join(buffer_dumps).replace("\n", "").replace(" ", "")


from spirvsmith_server_client.api.buffers import post_buffers
from spirvsmith_server_client.api.queues import register_executor
from spirvsmith_server_client.api.shaders import get_next_shader
from spirvsmith_server_client.models.buffer_submission import BufferSubmission
from spirvsmith_server_client.models.execution_platform import ExecutionPlatform as EP
from spirvsmith_server_client.models.retrieved_shader import RetrievedShader
from spirvsmith_server_client.types import Response

if __name__ == "__main__":
    execution_platform = ExecutionPlatform.auto_detect()
    execution_platform.display_summary()
    DumpMeta(
        key_transform="SNAKE",
    ).bind_to(ExecutionPlatform)
    input("Press enter to continue...")
    register_executor.sync(
        client=client, json_body=EP.from_dict(asdict(execution_platform))
    )
    while True:
        response: Response[RetrievedShader] = get_next_shader.sync_detailed(
            client=client, json_body=EP.from_dict(asdict(execution_platform))
        )
        if response.status_code == 404:
            time.sleep(2)
            continue

        retrieved_shader: RetrievedShader = response.parsed

        shader: SPIRVShader = parse_spirv_assembly_lines(
            retrieved_shader.shader_assembly.split("\n")
        )
        with tempfile.NamedTemporaryFile(suffix=".amber") as amber_file:
            create_amber_file(shader, amber_file.name)
            bindings: list[int] = sorted(
                map(
                    lambda b: b.extra_operands[0],
                    filter(
                        lambda a: isinstance(a, OpDecorate)
                        and a.decoration == Decoration.Binding,
                        list(shader.context.annotations.keys()),
                    ),
                )
            )
            buffer_dump: str = run_amber(
                amber_filename=amber_file.name,
                buffer_bindings=bindings,
                shader_id=retrieved_shader.shader_id,
            )
            if buffer_dump:
                buffer_submission: BufferSubmission = BufferSubmission(
                    executor=EP.from_dict(asdict(execution_platform)),
                    buffer_dump=buffer_dump,
                )
                post_buffers.sync(
                    shader_id=retrieved_shader.shader_id,
                    client=client,
                    json_body=buffer_submission,
                )
