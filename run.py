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
    n_types: int = 15
    n_constants: int = 10
    n_functions: int = 1
    max_depth: int = 3
    
    # Randomness parametrization (weights)
    w_memory_operation: int = 5
    w_logical_operation: int = 6
    w_arithmetic_operation: int = 6
    w_control_flow_operation: int = 1
    w_function_operation: int = 1
    w_bitwise_operation: int = 6
    p_statement: float = 0.98

cs = ConfigStore.instance()

cs.store(name="config", node=SPIRVSmithConfig)

@hydra.main(config_path="config", config_name="config")
def run(cfg: SPIRVSmithConfig) -> None:
    fuzzer: ShaderGenerator = ShaderGenerator(cfg)
    fuzzer.start()

if __name__ == "__main__":
    run()