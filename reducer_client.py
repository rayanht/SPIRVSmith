import subprocess
import time
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from tempfile import NamedTemporaryFile

from spirvsmith_server_client import Client
from spirvsmith_server_client.api.queues import get_queues
from spirvsmith_server_client.api.shaders import get_next_mismatch
from spirvsmith_server_client.models.shader_data import ShaderData
from spirvsmith_server_client.types import Response

from src.shader_parser import parse_spirv_assembly_file
from src.shader_parser import parse_spirv_assembly_lines
from src.shader_utils import disassemble_spv_file
from src.shader_utils import SPIRVShader


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
    def reduce(cls, shader_data: ShaderData) -> ReductionResult:
        shader: SPIRVShader = parse_spirv_assembly_lines(
            shader_data.shader_assembly.split("\n")
        )
        n_expected_reports: int = len(get_queues.sync(client=client).queues)

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
    client = Client(base_url="http://spirvsmith.hatout.dev")
    while True:
        response: Response[ShaderData] = get_next_mismatch.sync_detailed(client=client)
        if response.status_code == 404:
            time.sleep(2)
            continue

        shader_data: ShaderData = response.parsed
        shader_id: str = shader_data.shader_id
        print(f"Reducing shader {shader_id}")
        reduction_result: ReductionResult = SPIRVReducer.reduce(shader_data)
        if reduction_result.success:
            print(f"Shader {shader_id} successfully reduced.")
            reduction_result.reduced_shader.generate_assembly_file(
                f"interesting_shaders/{shader_id}.spasm"
            )
