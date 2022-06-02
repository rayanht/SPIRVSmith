import hydra
from hydra.core.config_store import ConfigStore

from config import SPIRVSmithConfig
from src.fuzzing_client import ShaderGenerator

cs = ConfigStore.instance()

cs.store(name="config", node=SPIRVSmithConfig)


@hydra.main(config_path="config", config_name="config", version_base=None)
def run(cfg: SPIRVSmithConfig) -> None:
    fuzzer: ShaderGenerator = ShaderGenerator(cfg)
    fuzzer.start()


if __name__ == "__main__":
    # pylint: disable = no-value-for-parameter
    run()
