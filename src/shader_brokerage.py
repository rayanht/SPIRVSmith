import pickle
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.fuzzing_server import SPIRVShader
from google.cloud import bigquery
from google.cloud import storage


STORAGE_CLIENT = storage.Client.from_service_account_json("infra/spirvsmith_gcp.json")
BQ_CLIENT = bigquery.Client.from_service_account_json("infra/spirvsmith_gcp.json")
BUCKET = STORAGE_CLIENT.get_bucket("spirv_shaders_bucket")


def upload_shader_to_gcs(shader: "SPIRVShader") -> None:
    pickled_shader: bytes = pickle.dumps(shader, protocol=pickle.HIGHEST_PROTOCOL)
    blob = BUCKET.blob(f"{shader.id}.pkl")
    blob.upload_from_string(pickled_shader)


def download_shader_from_gcs(shader_id: str) -> "SPIRVShader":
    blob = BUCKET.blob(f"{shader_id}.pkl")
    pickled_shader: str = blob.download_as_bytes()
    return pickle.loads(pickled_shader)


def insert_new_shader_into_BQ(shader: "SPIRVShader", generator_id: str) -> None:
    insert_query = f"""
        INSERT INTO `spirvsmith.spirv.shader_data`
        VALUES (
            "{shader.id}",
            1,
            "{generator_id}",
            "{shader.context.config.misc.version}",
            {len(shader.context.get_storage_buffers())},
            NULL,
            NULL,
            NULL,
            NULL,
            NULL,
            NULL,
            NULL
        )
    """
    BQ_CLIENT.query(insert_query).result()
