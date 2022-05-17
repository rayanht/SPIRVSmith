import argparse
import time
from tempfile import NamedTemporaryFile

import pandas as pd

from src.shader_brokerage import BQ_delete_shader
from src.shader_brokerage import BQ_fetch_reduced_buffer_dumps
from src.shader_brokerage import BQ_insert_new_shader
from src.shader_brokerage import GCS_upload_shader
from src.shader_parser import parse_spirv_assembly_file
from src.shader_utils import disassemble_spv_file
from src.shader_utils import SPIRVShader
from src.shader_utils import validate_spv_file


def is_interesting(spv_file_path: str, n_reports: int) -> int:
    if not validate_spv_file(spv_file_path):
        return 0
    with NamedTemporaryFile(suffix=".spasm") as disassembled_spasm_file:
        if not disassemble_spv_file(spv_file_path, disassembled_spasm_file.name):
            return 1
        parsed_shader: SPIRVShader = parse_spirv_assembly_file(
            disassembled_spasm_file.name
        )
        parsed_shader = parsed_shader.recondition().normalise_ids()
        if not parsed_shader.validate():
            return 1
        GCS_upload_shader(parsed_shader)
        BQ_insert_new_shader(parsed_shader, "reducer", high_priority=True)
        print(f"Inserted temporary shader with id {parsed_shader.id}")
        while True:
            buffer_dumps: pd.Series = (
                BQ_fetch_reduced_buffer_dumps(parsed_shader.id)
                .to_dataframe()
                .buffer_dump
            )
            print(
                f"Fetched {len(buffer_dumps)} reports. Expecting {n_reports - len(buffer_dumps)} more."
            )
            if len(buffer_dumps) >= n_reports:
                break
            time.sleep(5)
        BQ_delete_shader(parsed_shader.id)
        if not all(x == buffer_dumps[0] for x in buffer_dumps):
            return 0
        return 1


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("shader_id", help="Shader DB indentifier")
    argparser.add_argument("n_reports", help="Number of executor reports to wait for")
    argparser.add_argument("input_file", help="Path to a .spv file")
    args = argparser.parse_args()
    exit(is_interesting(args.input_file, int(args.n_reports)))
