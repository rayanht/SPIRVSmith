import argparse
import tempfile
import time
from tempfile import NamedTemporaryFile

import pandas as pd

from amber_client import run_amber
from src.shader_brokerage import BQ_delete_shader
from src.shader_brokerage import BQ_fetch_reduced_buffer_dumps
from src.shader_brokerage import BQ_insert_new_shader
from src.shader_brokerage import GCS_upload_shader
from src.shader_parser import parse_spirv_assembly_file
from src.shader_utils import create_amber_file
from src.shader_utils import disassemble_spv_file
from src.shader_utils import SPIRVShader
from src.shader_utils import validate_spv_file


def is_interesting(
    spv_file_path: str, shader_id: str, n_buffers: int, seed: int
) -> int:
    if not validate_spv_file(spv_file_path):
        return 1
    with NamedTemporaryFile(suffix=".spasm") as disassembled_spasm_file:
        if not disassemble_spv_file(spv_file_path, disassembled_spasm_file.name):
            return 1
        parsed_shader: SPIRVShader = parse_spirv_assembly_file(
            disassembled_spasm_file.name
        )
        parsed_shader = parsed_shader.recondition().normalise_ids()
        with tempfile.NamedTemporaryFile(suffix=".amber") as amber_file:
            create_amber_file(parsed_shader, amber_file.name, seed=seed)
            buffer_dump: str = run_amber(
                amber_filename=amber_file.name,
                n_buffers=n_buffers,
                shader_id=shader_id,
            )
            if buffer_dump == "SEGFAULT":
                return 0
        return 1


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("shader_id", help="Shader DB indentifier")
    argparser.add_argument("n_buffers", help="Number of buffers")
    argparser.add_argument("seed", help="Randomness seed")
    argparser.add_argument("input_file", help="Path to a .spv file")
    args = argparser.parse_args()
    exit(
        is_interesting(
            args.input_file, args.shader_id, int(args.n_buffers), int(args.seed)
        )
    )