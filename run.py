import json
from dataclasses import dataclass

import hydra
from hydra.core.config_store import ConfigStore

from src.fuzzing_server import ShaderGenerator


@dataclass
class BinariesConfig:
    ASSEMBLER_PATH: str = "bin/spirv-as"
    VALIDATOR_PATH: str = "bin/spirv-val"
    OPTIMISER_PATH: str = "bin/spirv-opt"
    AMBER_PATH: str = "bin/amber"


@dataclass
class LimitsConfig:
    n_types: int = 20
    n_constants: int = 50
    n_functions: int = 1
    max_depth: int = 3


@dataclass
class FuzzingStrategyConfig:
    ## Extensions
    enable_ext_glsl_std_450: bool = True

    ## Operations weights
    w_memory_operation: int = 4
    w_logical_operation: int = 4
    w_arithmetic_operation: int = 4
    w_control_flow_operation: int = 1
    w_function_operation: int = 1
    w_bitwise_operation: int = 4
    w_conversion_operation: int = 4
    w_composite_operation: int = 4

    ## Types weights
    w_scalar_type: int = 1
    w_numerical_type: int = 1
    w_container_type: int = 1
    w_arithmetic_type: int = 1

    ## Constants weights
    w_composite_constant: int = 1
    w_scalar_constant: int = 2

    # P(generating a statement at step t + 1 | a statement was generated at step t)
    p_statement: float = 0.995


@dataclass
class MiscConfig:
    start_web_server: bool = False
    broadcast_generated_shaders: bool = False


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
