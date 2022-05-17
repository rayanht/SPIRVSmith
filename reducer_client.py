import subprocess
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from enum import auto
from enum import Enum
from tempfile import NamedTemporaryFile

import pandas as pd

from src.shader_brokerage import BQ_fetch_mismatched_shaders
from src.shader_brokerage import GCS_download_shader
from src.shader_parser import parse_spirv_assembly_file
from src.shader_utils import disassemble_spv_file
from src.shader_utils import SPIRVShader


@dataclass
class ReductionTarget:
    shader_id: str
    shader_data: pd.DataFrame


@dataclass
class ReductionResult:
    success: bool
    reduced_shader: SPIRVShader


class ProgramReducer(ABC):
    @abstractmethod
    def reduce(self, shader: SPIRVShader) -> ReductionResult:
        ...


class SPIRVReducer(ProgramReducer):
    @classmethod
    def reduce(cls, target: ReductionTarget) -> ReductionResult:
        shader: SPIRVShader = GCS_download_shader(target.shader_id)
        n_expected_reports: int = len(target.shader_data)
        with NamedTemporaryFile(suffix=".spv") as spv_in_file:
            with NamedTemporaryFile(suffix=".spv") as spv_out_file:
                if not shader.assemble(spv_in_file.name):
                    return ReductionResult(False, shader)
                reduce_process: subprocess.CompletedProcess = subprocess.run(
                    [
                        "spirv-reduce",
                        spv_in_file.name,
                        "-o",
                        spv_out_file.name,
                        "--",
                        f"./scripts/interestingness.sh",
                        shader.id,
                        str(n_expected_reports),
                    ],
                    capture_output=False,
                )
                if reduce_process.returncode != 0:
                    print(reduce_process.stderr.decode("utf-8"))
                    return ReductionResult(False, shader)
                with NamedTemporaryFile(
                    suffix=".spasm"
                ) as disassembled_reduced_spasm_file:
                    if not disassemble_spv_file(
                        spv_out_file.name,
                        disassembled_reduced_spasm_file.name,
                    ):
                        return ReductionResult(False, shader)
                    parsed_shader: SPIRVShader = parse_spirv_assembly_file(
                        disassembled_reduced_spasm_file.name
                    )
                    return ReductionResult(True, parsed_shader)


if __name__ == "__main__":
    while True:
        mismatched_shaders: pd.DataFrame = BQ_fetch_mismatched_shaders().to_dataframe()
        unique_mismatches: list[str] = mismatched_shaders.shader_id.unique()
        print(
            f"Found {len(mismatched_shaders)} mismatched shaders ({len(unique_mismatches)} unique)"
        )
        print(mismatched_shaders)
        for shader_id in unique_mismatches:
            print(f"Reducing shader {shader_id}")
            reduction_target: ReductionTarget = ReductionTarget(
                shader_id,
                mismatched_shaders[mismatched_shaders.shader_id == shader_id].drop(
                    ["shader_id"], axis=1
                ),
            )
            reduction_result: ReductionResult = SPIRVReducer.reduce(reduction_target)
            if reduction_result.success:
                print(f"Shader {shader_id} successfully reduced.")
                reduction_result.reduced_shader.generate_assembly_file(
                    f"interesting_shaders/{shader_id}.spasm"
                )
            exit(0)
