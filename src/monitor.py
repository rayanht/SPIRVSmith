import logging
from enum import Enum
from typing import Optional
from typing import TYPE_CHECKING

import daiquiri

if TYPE_CHECKING:
    from run import SPIRVSmithConfig

from src.utils import get_spirvsmith_version

LOG_VERSION: str = get_spirvsmith_version()


class Event(Enum):
    AMBER_SUCCESS = "AMBER_SUCCESS"
    AMBER_FAILURE = "AMBER_FAILURE"
    AMBER_SEGFAULT = "AMBER_SEGFAULT"
    ASSEMBLER_SUCCESS = "ASSEMBLER_SUCCESS"
    ASSEMBLER_FAILURE = "ASSEMBLER_FAILURE"
    DISASSEMBLER_SUCCESS = "DISASSEMBLER_SUCCESS"
    DISASSEMBLER_FAILURE = "DISASSEMBLER_FAILURE"
    OPTIMIZER_SUCCESS = "OPTIMIZER_SUCCESS"
    OPTIMIZER_FAILURE = "OPTIMIZER_FAILURE"
    VALIDATOR_SUCCESS = "VALIDATOR_SUCCESS"
    VALIDATOR_FAILURE = "VALIDATOR_FAILURE"
    VALIDATOR_OPT_SUCCESS = "VALIDATOR_OPT_SUCCESS"
    VALIDATOR_OPT_FAILURE = "VALIDATOR_OPT_FAILURE"
    GCS_UPLOAD_SUCCESS = "GCS_UPLOAD_SUCCESS"
    GENERATOR_MUTATION = "GENERATOR_MUTATION"
    BQ_GENERATOR_REGISTRATION_SUCCESS = "BQ_GENERATOR_REGISTRATION_SUCCESS"
    BQ_GENERATOR_REGISTRATION_FAILURE = "BQ_GENERATOR_REGISTRATION_FAILURE"
    BQ_SHADER_DATA_UPSERT_SUCCESS = "BQ_SHADER_DATA_UPSERT_SUCCESS"
    BQ_SHADER_DATA_UPSERT_FAILURE = "BQ_SHADER_DATA_UPSERT_FAILURE"
    NO_OPERAND_FOUND = "NO_OPERAND_FOUND"
    TERMINATED = "TERMINATED"
    INVALID_TYPE_AMBER_BUFFER = "INVALID_TYPE_AMBER_BUFFER"
    PAUSED = "PAUSED"
    DEBUG = "DEBUG"


class Monitor:
    def __init__(self, config: Optional["SPIRVSmithConfig"] = None) -> None:
        outputs = [
            daiquiri.output.Stream(
                formatter=daiquiri.formatter.ColorFormatter(
                    fmt=("[%(levelname)s] [%(asctime)s] %(message)s")
                ),
                level=logging.WARNING,
            )
        ]
        if config and config.misc.upload_logs:
            outputs.append(daiquiri.output.Datadog(level=logging.INFO))
        daiquiri.setup(
            outputs=outputs,
        )

        self.logger = daiquiri.getLogger(__name__)

    def debug(self, event: Event, extra: dict[str, str] = None) -> None:
        if not extra:
            extra = {}
        extra["version"] = LOG_VERSION
        extra["tag"] = event.value
        self.logger.debug(event.value, extra=extra)

    def info(self, event: Event, extra: dict[str, str] = None) -> None:
        if not extra:
            extra = {}
        extra["version"] = LOG_VERSION
        extra["tag"] = event.value
        self.logger.info(event.value, extra=extra)

    def warning(self, event: Event, extra: dict[str, str] = None) -> None:
        if not extra:
            extra = {}
        extra["version"] = LOG_VERSION
        extra["tag"] = event.value
        self.logger.warning(event.value, extra=extra)

    def error(self, event: Event, extra: dict[str, str] = None) -> None:
        if not extra:
            extra = {}
        extra["version"] = LOG_VERSION
        extra["tag"] = event.value
        self.logger.error(event.value, extra=extra)
