import argparse
import os
import random
import subprocess

SPIRV_CROSS_PATH = "bin/spirv-cross"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--target", help="MSL or GLSL", nargs="?", choices=("msl", "glsl")
    )
    args = parser.parse_args()

    shader_path = f"out/{random.choice(os.listdir('out/'))}/shader.spv"
    if args.target == "msl":
        process: subprocess.CompletedProcess = subprocess.run(
            [
                SPIRV_CROSS_PATH,
                "--msl",
                shader_path,
            ],
            capture_output=True,
        )
        print(process.stdout.decode("utf-8"))
    elif args.target == "glsl":
        process: subprocess.CompletedProcess = subprocess.run(
            [
                SPIRV_CROSS_PATH,
                "--es",
                shader_path,
            ],
            capture_output=True,
        )
        print(process.stdout.decode("utf-8"))
