from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING

import dill

from src.execution_platform import ExecutionPlatform
from src.shader_parser import parse_spirv_assembly_file
from src.utils import get_spirvsmith_version

if TYPE_CHECKING:
    from src.fuzzing_server import SPIRVShader
from google.cloud import bigquery
from google.cloud import storage
from google.cloud.bigquery.job import QueryJob
from google.cloud.bigquery.table import RowIterator
import sys

if "pytest" not in sys.modules:
    STORAGE_CLIENT = storage.Client.from_service_account_json(
        "infra/spirvsmith_gcp.json"
    )
    BQ_CLIENT = bigquery.Client.from_service_account_json("infra/spirvsmith_gcp.json")
    BUCKET = STORAGE_CLIENT.get_bucket("spirv_shaders_bucket")


def GCS_upload_shader(shader: "SPIRVShader") -> None:
    with NamedTemporaryFile(suffix=".spasm") as f:
        shader.generate_assembly_file(f.name)
        blob = BUCKET.blob(f"{shader.id}.spasm")
        blob.upload_from_filename(f.name)


def GCS_download_shader(shader_id: str) -> "SPIRVShader":
    with NamedTemporaryFile(suffix=".spasm") as f:
        blob = BUCKET.blob(f"{shader_id}.spasm")
        blob.download_to_filename(f.name)
        return parse_spirv_assembly_file(f.name)


def BQ_insert_new_shader(
    shader: "SPIRVShader", generator_id: str, high_priority: bool = False
) -> None:
    insert_query = f"""
        INSERT INTO `spirvsmith.spirv.shader_data`
        VALUES (
            "{shader.id}",
            {1 if high_priority else 0},
            "{generator_id}",
            "{shader.context.config.misc.version}",
            {len(shader.context.get_storage_buffers())},
            NULL,
            NULL,
            NULL,
            NULL,
            NULL,
            NULL,
            NULL,
            CURRENT_TIMESTAMP()
        )
    """
    BQ_CLIENT.query(insert_query).result()


def BQ_update_shader_with_buffer_dumps(
    original_entry,
    execution_platform: ExecutionPlatform,
    shader_id: str,
    buffer_dump: str,
) -> None:
    insert_query = f"""
    INSERT INTO `spirvsmith.spirv.shader_data`
    VALUES (
        "{shader_id}",
        {original_entry.execution_priority},
        "{original_entry.generator_id}",
        "{original_entry.generator_version}",
        {original_entry.n_buffers},
        "{buffer_dump}",
        "{execution_platform.operating_system.value}",
        "{execution_platform.get_active_hardware().hardware_type.value}",
        "{execution_platform.get_active_hardware().hardware_vendor.value}",
        "{execution_platform.get_active_hardware().hardware_model}",
        "{execution_platform.get_active_hardware().driver_version}",
        "{execution_platform.vulkan_backend.value}",
        CURRENT_TIMESTAMP()
    )
    """
    delete_query = f"""
        DELETE FROM
        `spirvsmith.spirv.shader_data`
        WHERE shader_id = "{shader_id}" AND buffer_dump IS NULL AND platform_os IS NULL
    """
    BQ_CLIENT.query(insert_query).result()
    BQ_CLIENT.query(delete_query).result()


def BQ_fetch_shaders_pending_execution(
    execution_platform: ExecutionPlatform,
) -> RowIterator:
    fetch_query: str = f"""
        SELECT
        *
        FROM
        `spirvsmith.spirv.shader_data`
        WHERE
        (platform_os != "{execution_platform.operating_system.value}"
        OR platform_os IS NULL)
        AND (platform_hardware_type != "{execution_platform.get_active_hardware().hardware_type.value}"
        OR platform_hardware_type IS NULL)
        AND (platform_backend != "{execution_platform.vulkan_backend.value}"
        OR platform_backend IS NULL)
        OR (platform_os = "{execution_platform.operating_system.value}"
        AND platform_hardware_type = "{execution_platform.get_active_hardware().hardware_type.value}"
        AND platform_backend = "{execution_platform.vulkan_backend.value}"
        AND buffer_dump IS NULL)
        AND generator_version = "{get_spirvsmith_version()}"
        ORDER BY execution_priority DESC, insertion_time ASC
    """
    query_job: QueryJob = BQ_CLIENT.query(fetch_query)
    return query_job.result()


def BQ_fetch_mismatched_shaders() -> RowIterator:
    mismatches_query: str = f"""
    SELECT
    t1.shader_id,
    n_buffers,
    buffer_dump,
    platform_os,
    platform_hardware_type,
    platform_hardware_vendor,
    platform_hardware_model,
    platform_hardware_driver_version,
    platform_backend,
    generator_id,
    generator_version
    FROM (
    SELECT
        shader_id,
        ARRAY_AGG(buffer_dump) AS dumps,
        MIN(buffer_dump) AS mn,
        MAX(buffer_dump) AS mx
    FROM
        `spirvsmith.spirv.shader_data`
    WHERE
        buffer_dump IS NOT NULL
    GROUP BY
        shader_id
    HAVING
        mn != mx) AS t1
    JOIN
    `spirvsmith.spirv.shader_data` AS t2
    ON
    t1.shader_id = t2.shader_id
    WHERE
    buffer_dump IS NOT NULL
    AND generator_version = "{get_spirvsmith_version()}"
    ORDER BY
    shader_id
    """
    query_job: QueryJob = BQ_CLIENT.query(mismatches_query)
    return query_job.result()


def BQ_fetch_reduced_buffer_dumps(shader_id: str) -> RowIterator:
    fetch_query: str = f"""
        SELECT
        *
        FROM
        `spirvsmith.spirv.shader_data`
        WHERE
        shader_id = "{shader_id}"
        AND buffer_dump IS NOT NULL
        AND generator_id = "reducer"
    """
    query_job: QueryJob = BQ_CLIENT.query(fetch_query)
    return query_job.result()


def BQ_delete_shader(shader_id: str) -> None:
    delete_query = f"""
        DELETE FROM
        `spirvsmith.spirv.shader_data`
        WHERE
        shader_id = "{shader_id}"
    """
    BQ_CLIENT.query(delete_query).result()
