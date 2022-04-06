from dataclasses import dataclass

import hydra
from hydra.core.config_store import ConfigStore

from fuzzer import ShaderGenerator


@dataclass
class SPIRVSmithConfig:
    # Binaries
    ASSEMBLER_PATH: str = "bin/spirv-as"
    VALIDATOR_PATH: str = "bin/spirv-val"
    OPTIMISER_PATH: str = "bin/spirv-opt"
    AMBER_PATH: str = "bin/amber"

    # Limits
    n_types: int = 10
    n_constants: int = 15
    n_functions: int = 1
    max_depth: int = 3

    # Randomness parametrization (weights)
    ## Operations weights
    w_memory_operation: int = 4
    w_logical_operation: int = 8
    w_arithmetic_operation: int = 8
    w_control_flow_operation: int = 0
    w_function_operation: int = 1
    w_bitwise_operation: int = 8
    w_conversion_operation: int = 8

    ## Types weights
    w_scalar_type: int = 1
    w_numerical_type: int = 1
    w_container_type: int = 1
    w_arithmetic_type: int = 1

    # Randomness parametrization (probabilities)
    p_statement: float = 0.999


cs = ConfigStore.instance()

cs.store(name="config", node=SPIRVSmithConfig)


@hydra.main(config_path="config", config_name="config")
def run(cfg: SPIRVSmithConfig) -> None:
    fuzzer: ShaderGenerator = ShaderGenerator(cfg)
    fuzzer.start()


if __name__ == "__main__":
    run()
