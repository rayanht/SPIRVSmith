import random
from dataclasses import dataclass

import hydra
from hydra.core.config_store import ConfigStore

from src.fuzzing_server import ShaderGenerator
from src.utils import ClampedInt
from src.utils import get_spirvsmith_version


@dataclass
class BinariesConfig:
    ASSEMBLER_PATH: str = "bin/spirv-as"
    VALIDATOR_PATH: str = "bin/spirv-val"
    OPTIMISER_PATH: str = "bin/spirv-opt"
    CROSS_PATH: str = "bin/spirv-cross"
    AMBER_PATH: str = "bin/amber"


@dataclass
class MutationsConfig:
    ## Operations weights
    w_memory_operation: tuple[int, int] = (2, 6)
    w_logical_operation: tuple[int, int] = (2, 6)
    w_arithmetic_operation: tuple[int, int] = (2, 6)
    w_control_flow_operation: tuple[int, int] = (0, 2)
    w_function_operation: tuple[int, int] = (1, 1)
    w_bitwise_operation: tuple[int, int] = (2, 6)
    w_conversion_operation: tuple[int, int] = (2, 6)
    w_composite_operation: tuple[int, int] = (2, 6)

    ## Types weights
    w_scalar_type: tuple[int, int] = (1, 3)
    w_container_type: tuple[int, int] = (1, 3)

    ## Constants weights
    w_composite_constant: tuple[int, int] = (1, 3)
    w_scalar_constant: tuple[int, int] = (2, 4)


@dataclass
class LimitsConfig:
    n_types: int = 20
    n_constants: int = 50
    n_functions: int = 1
    max_depth: int = 3


@dataclass
class FuzzingStrategyConfig:
    ## Mutations
    mutations_config: MutationsConfig = MutationsConfig()

    ## Extensions
    enable_ext_glsl_std_450: bool = True

    ## Operations weights
    w_memory_operation: int = random.SystemRandom().randint(
        *mutations_config.w_memory_operation
    )
    w_logical_operation: int = random.SystemRandom().randint(
        *mutations_config.w_logical_operation
    )
    w_arithmetic_operation: int = random.SystemRandom().randint(
        *mutations_config.w_arithmetic_operation
    )
    w_control_flow_operation: int = random.SystemRandom().randint(
        *mutations_config.w_control_flow_operation
    )
    w_function_operation: int = random.SystemRandom().randint(
        *mutations_config.w_function_operation
    )
    w_bitwise_operation: int = random.SystemRandom().randint(
        *mutations_config.w_bitwise_operation
    )
    w_conversion_operation: int = random.SystemRandom().randint(
        *mutations_config.w_conversion_operation
    )
    w_composite_operation: int = random.SystemRandom().randint(
        *mutations_config.w_composite_operation
    )

    ## Types weights
    w_scalar_type: int = random.SystemRandom().randint(*mutations_config.w_scalar_type)
    w_container_type: int = random.SystemRandom().randint(
        *mutations_config.w_container_type
    )

    ## Constants weights
    w_composite_constant: int = random.SystemRandom().randint(
        *mutations_config.w_composite_constant
    )
    w_scalar_constant: int = random.SystemRandom().randint(
        *mutations_config.w_scalar_constant
    )

    # P(generating a statement at step t + 1 | a statement was generated at step t)
    p_statement: float = 0.995

    # Number of optimiser fuzzing iterations
    optimiser_fuzzing_iterations: int = 20

    # Strategy mutation parameters
    # When a mutation is triggered, one random parameter from FuzzingStrategyConfig
    # is chosen and slightly altered
    mutation_rate: float = 0.05


@dataclass
class MiscConfig:
    start_web_server: bool = False
    broadcast_generated_shaders: bool = True
    upload_logs: bool = True
    version: str = get_spirvsmith_version()


@dataclass
class SPIRVSmithConfig:
    # Binaries
    binaries: BinariesConfig = BinariesConfig()

    # Limits
    limits: LimitsConfig = LimitsConfig()

    # Fuzzing strategy
    strategy: FuzzingStrategyConfig = FuzzingStrategyConfig()

    # Misc
    misc: MiscConfig = MiscConfig()


cs = ConfigStore.instance()

cs.store(name="config", node=SPIRVSmithConfig)


@hydra.main(config_path="config", config_name="config")
def run(cfg: SPIRVSmithConfig) -> None:
    fuzzer: ShaderGenerator = ShaderGenerator(cfg)
    fuzzer.start()


if __name__ == "__main__":
    # pylint: disable = no-value-for-parameter
    run()
