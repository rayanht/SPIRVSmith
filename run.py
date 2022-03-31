from dataclasses import dataclass

import hydra
from hydra.core.config_store import ConfigStore

from fuzzer import ShaderGenerator

@dataclass
class SPIRVSmithConfig:
    ASSEMBLER_PATH: str = "bin/spirv-as"
    VALIDATOR_PATH: str = "bin/spirv-val"
    OPTIMISER_PATH: str = "bin/spirv-opt"
    AMBER_PATH: str = "bin/amber"
    
    n_types: int = 10
    n_constants: int = 4
    n_functions: int = 1
    max_depth: int = 3

cs = ConfigStore.instance()

cs.store(name="config", node=SPIRVSmithConfig)

@hydra.main(config_path="config", config_name="config")
def run(cfg: SPIRVSmithConfig) -> None:
    fuzzer: ShaderGenerator = ShaderGenerator(cfg)
    fuzzer.start()

if __name__ == "__main__":
    run()