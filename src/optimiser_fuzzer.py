import signal
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from random import SystemRandom
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.fuzzing_server import SPIRVShader
from src.monitor import Event, Monitor

SPIRV_OPTIMISER_FLAGS = [
    "--amd-ext-to-khr",
    "--before-hlsl-legalization",
    "--ccp",
    "--cfg-cleanup",
    "--combine-access-chains",
    "--compact-ids",
    "--convert-local-access-chains",
    "--convert-relaxed-to-half",
    "--copy-propagate-arrays",
    "--replace-desc-array-access-using-var-index",
    "--spread-volatile-semantics",
    "--eliminate-dead-branches",
    "--eliminate-dead-code-aggressive",
    "--eliminate-dead-const",
    "--eliminate-dead-functions",
    "--eliminate-dead-inserts",
    "--eliminate-dead-variables",
    "--eliminate-local-multi-store",
    "--eliminate-local-single-block",
    "--eliminate-local-single-store",
    "--flatten-decorations",
    "--fold-spec-const-op-composite",
    "--graphics-robust-access",
    "--if-conversion",
    "--inline-entry-points-exhaustive",
    "--local-redundancy-elimination",
    "--loop-invariant-code-motion",
    "--loop-unroll",
    "--loop-peeling",
    "--merge-blocks",
    "--merge-return",
    "--loop-unswitch",
    "--private-to-local",
    "--redundancy-elimination",
    "--simplify-instructions",
    "--strength-reduction",
    "--upgrade-memory-model",
    "--vector-dce",
    "--unify-const",
]


def fuzz_optimiser(shader: "SPIRVShader"):
    with tempfile.NamedTemporaryFile(suffix=".spv") as spv_file:
        if shader.assemble(spv_file.name, silent=True) and shader.validate(silent=True):
            with ThreadPoolExecutor(max_workers=4) as executor:
                for _ in range(
                    shader.context.config.strategy.optimiser_fuzzing_iterations
                ):
                    executor.submit(_fuzz_optimiser, shader, spv_file.name)


def _fuzz_optimiser(shader: "SPIRVShader", filename: str):
    spirv_opt_flags: list[str] = SystemRandom().choices(
        SPIRV_OPTIMISER_FLAGS, k=SystemRandom().randint(5, len(SPIRV_OPTIMISER_FLAGS))
    )
    process: subprocess.CompletedProcess = subprocess.run(
        [
            shader.context.config.binaries.OPTIMISER_PATH,
            "--target-env=spv1.3",
            *spirv_opt_flags,
            filename,
            "-o",
            f"/dev/null",
        ],
        capture_output=True,
    )
    if process.returncode != 0:
        Monitor(shader.context.config).error(
            event=Event.OPTIMIZER_FAILURE,
            extra={
                "stderr": process.stderr.decode("utf-8"),
                "stdout": process.stdout.decode("utf-8"),
                "is_segfault": process.returncode == -signal.SIGSEGV,
                "run_args": " ".join(process.args),
                "shader_id": shader.id,
                "spirv-opt_flags": spirv_opt_flags,
            },
        )
    else:
        Monitor(shader.context.config).info(
            event=Event.OPTIMIZER_SUCCESS,
            extra={"shader_id": shader.id, "spirv-opt_flags": spirv_opt_flags},
        )
