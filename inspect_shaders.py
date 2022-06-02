import argparse
import os
import random
import subprocess
from tempfile import NamedTemporaryFile

from src.shader_utils import assemble_spasm_file

SPIRV_CROSS_PATH = "spirv-cross"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--target", help="MSL or GLSL", nargs="?", choices=("msl", "glsl")
    )
    args = parser.parse_args()

    shader_path = f"out/{random.SystemRandom().choice(os.listdir('out/'))}"
    with NamedTemporaryFile(suffix=".spv") as assembled_spirv_file:
        assemble_spasm_file(shader_path, assembled_spirv_file.name)
        if args.target == "msl":
            process: subprocess.CompletedProcess = subprocess.run(
                [
                    SPIRV_CROSS_PATH,
                    "--msl",
                    assembled_spirv_file.name,
                ],
                capture_output=False,
            )
        elif args.target == "glsl":
            process: subprocess.CompletedProcess = subprocess.run(
                [
                    SPIRV_CROSS_PATH,
                    "--es",
                    assembled_spirv_file.name,
                ],
                capture_output=False,
            )
