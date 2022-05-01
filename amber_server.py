import platform
import subprocess
from functools import reduce
from itertools import repeat
from operator import iconcat

import GPUtil
from cpuinfo import get_cpu_info
from google.cloud import bigquery
from google.cloud import storage

from src.monitor import Event
from src.monitor import Monitor

AMBER_PATH = "bin/amber"

VK_ICD_FILENAMES_SWIFTSHADER = (
    "/Users/rayan/swiftshader/build/Darwin/vk_swiftshader_icd.json"
)
VK_ICD_FILENAMES_MOLTENVK = (
    "/Users/rayan/VulkanSDK/1.3.204.1/macOS/share/vulkan/icd.d/MoltenVK_icd.json"
)

MONITOR = Monitor()

STORAGE_CLIENT = storage.Client.from_service_account_json("infra/spirvsmith_gcp.json")
BQ_CLIENT = bigquery.Client.from_service_account_json("infra/spirvsmith_gcp.json")
BUCKET = STORAGE_CLIENT.get_bucket("spirv_shaders_bucket")


def get_pending_shaders_query(
    platform_os: str, platform_hardware_vendor: str, platform_backend: str
) -> str:
    return f"""
        SELECT
        *
        FROM
        `spirvsmith.spirv.shader_data`
        WHERE
        platform_os != "{platform_os}"
        OR platform_os IS NULL
        AND platform_hardware_type != "{platform_hardware_vendor}"
        OR platform_hardware_type IS NULL
        AND platform_backend != "{platform_backend}"
        OR platform_backend IS NULL
    """


def fetch_amber_file_from_GCS(shader_id: str) -> None:
    print(f"Fetching shader {shader_id} from GCS...")
    blob = BUCKET.blob(f"{shader_id}/out.amber")
    blob.download_to_filename("tmp.amber")


def insert_BQ_entry(
    original_entry,
    platform_os: str,
    hardware_type: str,
    hardware_vendor: str,
    hardware_driver_version: str,
    backend: str,
    shader_id: str,
    buffer_dump: str,
) -> None:
    errors = BQ_CLIENT.insert_rows_json(
        "spirvsmith.spirv.shader_data",
        [
            {
                "shader_id": shader_id,
                "n_buffers": original_entry.n_buffers,
                "generator_id": original_entry.generator_id,
                "generator_version": original_entry.generator_version,
                "buffer_dump": buffer_dump,
                "platform_os": platform_os,
                "platform_hardware_type": hardware_type,
                "platform_hardware_vendor": hardware_vendor,
                "platform_hardware_model": hardware_model,
                "platform_hardware_driver_version": hardware_driver_version,
                "platform_backend": backend,
            }
        ],
    )
    if not errors == []:
        MONITOR.error(
            event=Event.BQ_SHADER_DATA_UPSERT_FAILURE,
            extra={
                "errors": errors,
            },
        )

    query = f"""
        DELETE FROM
        `spirvsmith.spirv.shader_data`
        WHERE shader_id = {shader_id} AND buffer_dump IS NULL
    """
    BQ_CLIENT.query(query)


def run_amber(n_buffers: int, shader_id: str) -> str:
    process: subprocess.CompletedProcess = subprocess.run(
        [
            AMBER_PATH,
            "-t",
            "spv1.3",
            "-v",
            "1.2",
            "-b",
            "out.txt",
            *reduce(
                iconcat,
                zip(repeat("-B"), [f"pipeline:0:{i}" for i in range(n_buffers)]),
                [],
            ),
            "tmp.amber",
        ],
        capture_output=True,
    )
    if process.stderr:
        print(process.stderr.decode("utf-8"))
        MONITOR.error(
            event=Event.AMBER_FAILURE,
            extra={
                "stderr": process.stderr.decode("utf-8"),
                "cli_args": str(process.args),
                "shader_id": shader_id,
            },
        )
        return None

    MONITOR.info(event=Event.AMBER_SUCCESS, extra={"shader_id": shader_id})

    with open("out.txt", "r") as f:
        buffer_dumps: list[str] = list(
            filter(lambda l: not l.startswith("pipeline"), f.readlines())
        )
        buffer_dumps: list[str] = [d.strip().replace(" ", "") for d in buffer_dumps]
        return " ".join(buffer_dumps)


if __name__ == "__main__":
    platform_os = platform.system()
    if platform_os == "Darwin":
        backend = "MoltenVK"
    elif platform_os == "Linux":
        backend = "Vulkan"
    print(f"Detected platform OS -> {platform_os}")
    nvidia_gpus = GPUtil.getGPUs()
    cpu_info = get_cpu_info()
    cpu_name = cpu_info["brand_raw"]
    if nvidia_gpus:
        print(f"Detected NVIDIA GPUs         -> {nvidia_gpus}")
    print(f"Detected CPU         -> {cpu_name}")
    if not nvidia_gpus:
        print("Amber will run on CPU")
        hardware_type = "CPU"
        hardware_vendor = cpu_info["vendor_id_raw"]
        hardware_model = cpu_name
        hardware_driver_version = "N/A"
    else:
        print(f"Amber will run on {nvidia_gpus[0]}")
        hardware_type = "GPU"
        hardware_vendor = "NVIDIA"
        hardware_model = nvidia_gpus[0].name
        hardware_driver_version = nvidia_gpus[0].driver

    while True:
        query_job = BQ_CLIENT.query(
            get_pending_shaders_query(platform_os, hardware_vendor, backend)
        )
        n_pending_shaders = query_job.result().total_rows
        print(
            f"Found {n_pending_shaders} pending shaders for {platform_os}/{hardware_vendor}/{backend}"
        )
        for row in query_job:
            fetch_amber_file_from_GCS(row.shader_id)
            buffer_dump: str = run_amber(
                n_buffers=row.n_buffers, shader_id=row.shader_id
            )
            if buffer_dump:
                insert_BQ_entry(
                    row,
                    platform_os,
                    hardware_type,
                    hardware_vendor,
                    hardware_driver_version,
                    backend,
                    row.shader_id,
                    buffer_dump,
                )
