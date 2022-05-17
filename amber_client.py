import signal
import subprocess
import tempfile
from functools import reduce
from itertools import repeat
from operator import iconcat

import pandas as pd
from google.api_core.exceptions import NotFound
from google.cloud.bigquery.table import RowIterator

from run import *
from src.execution_platform import ExecutionPlatform
from src.monitor import Event
from src.monitor import Monitor
from src.shader_brokerage import BQ_delete_shader
from src.shader_brokerage import BQ_fetch_shaders_pending_execution
from src.shader_brokerage import BQ_get_high_priority_shader_ids
from src.shader_brokerage import BQ_update_shader_with_buffer_dumps
from src.shader_brokerage import GCS_download_shader
from src.shader_utils import create_amber_file
from src.shader_utils import SPIRVShader

AMBER_PATH = "bin/amber"

MONITOR = Monitor()

terminate = False


def signal_handling(signum, frame):
    global terminate
    terminate = True


signal.signal(signal.SIGINT, signal_handling)


def run_amber(amber_filename: str, n_buffers: int, shader_id: str) -> str:
    with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
        process: subprocess.CompletedProcess = subprocess.run(
            [
                AMBER_PATH,
                "-t",
                "spv1.3",
                "-v",
                "1.2",
                "-b",
                temp_file.name,
                *reduce(
                    iconcat,
                    zip(repeat("-B"), [f"pipeline:0:{i}" for i in range(n_buffers)]),
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
            buffer_dumps: list[str] = [d.strip().replace(" ", "") for d in buffer_dumps]
            return " ".join(buffer_dumps)


if __name__ == "__main__":
    execution_platform = ExecutionPlatform.auto_detect()
    execution_platform.display_summary()
    input("Press enter to continue...")
    while True:
        pending_shaders: pd.DataFrame = BQ_fetch_shaders_pending_execution(
            execution_platform
        )
        current_shader_set: set[str] = set(pending_shaders.shader_id)
        print(
            f"Found {len(pending_shaders)} pending shaders for {str(execution_platform)}"
        )
        for _, row in pending_shaders.iterrows():
            try:
                shader: SPIRVShader = GCS_download_shader(row.shader_id)
            except NotFound:
                print(f"No GCS entry found for shader {row.shader_id}")
                BQ_delete_shader(row.shader_id)
            with tempfile.NamedTemporaryFile(suffix=".amber") as amber_file:
                create_amber_file(
                    shader, amber_file.name, seed=row.buffer_initialisation_seed
                )
                buffer_dump: str = run_amber(
                    amber_filename=amber_file.name,
                    n_buffers=row.n_buffers,
                    shader_id=row.shader_id,
                )
                if buffer_dump:
                    BQ_update_shader_with_buffer_dumps(
                        row, execution_platform, row.shader_id, buffer_dump
                    )
            high_priority_shader_set: set[str] = BQ_get_high_priority_shader_ids()
            if not all(
                [shader in current_shader_set for shader in high_priority_shader_set]
            ):
                print(
                    "Detected high priority shaders not in current execution queue, refreshing..."
                )
                break
            if terminate:
                break
        if terminate:
            break
