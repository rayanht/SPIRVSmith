import argparse
from tempfile import NamedTemporaryFile

from src.shader_parser import parse_spirv_assembly_file
from src.shader_utils import disassemble_spv_file
from src.shader_utils import SPIRVShader
from src.shader_utils import validate_spv_file


def is_interesting(spv_file_path: str) -> int:
    if not validate_spv_file(spv_file_path):
        return 0
    with NamedTemporaryFile(suffix=".spasm") as disassembled_spasm_file:
        if not disassemble_spv_file(
            spv_file_path, disassembled_spasm_file.name, silent=True
        ):
            return 0
        parsed_shader: SPIRVShader = parse_spirv_assembly_file(
            disassembled_spasm_file.name
        )
        parsed_shader = parsed_shader.recondition().normalise_ids()
        if parsed_shader.validate(silent=True):
            return 0


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("input_file", help="Path to a .spv file")
    argparser.add_argument("shader_id", help="Shader DB indentifier")
    args = argparser.parse_args()
    exit(is_interesting(args.input_file))
