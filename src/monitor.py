import logging
from enum import Enum

import daiquiri

# Eventually should do this automatically with the package version
LOG_VERSION: float = 0.5

import socket


def is_gce_instance():
    """Check if running in a GCE instance via DNS lookup to metadata server."""
    try:
        socket.getaddrinfo("metadata.google.internal", 80)
    except socket.gaierror:
        return False
    return True


class Event(Enum):
    AMBER_SUCCESS = "AMBER_SUCCESS"
    AMBER_FAILURE = "AMBER_FAILURE"
    ASSEMBLER_SUCCESS = "ASSEMBLER_SUCCESS"
    ASSEMBLER_FAILURE = "ASSEMBLER_FAILURE"
    OPTIMIZER_SUCCESS = "OPTIMIZER_SUCCESS"
    OPTIMIZER_FAILURE = "OPTIMIZER_FAILURE"
    VALIDATOR_SUCCESS = "VALIDATOR_SUCCESS"
    VALIDATOR_FAILURE = "VALIDATOR_FAILURE"
    VALIDATOR_OPT_SUCCESS = "VALIDATOR_OPT_SUCCESS"
    VALIDATOR_OPT_FAILURE = "VALIDATOR_OPT_FAILURE"
    SHADER_UPLOAD_SUCCESS = "SHADER_UPLOAD_SUCCESS"
    SHADER_PUBSUB_SUCCESS = "SHADER_PUBSUB_SUCCESS"
    NO_OPERAND_FOUND = "NO_OPERAND_FOUND"
    TERMINATED = "TERMINATED"
    INVALID_TYPE_AMBER_BUFFER = "INVALID_TYPE_AMBER_BUFFER"
    PAUSED = "PAUSED"
    DEBUG = "DEBUG"


class Monitor:
    def __init__(self) -> None:
        outputs = [daiquiri.output.Datadog()]
        if not is_gce_instance():
            outputs.append(
                daiquiri.output.Stream(
                    formatter=daiquiri.formatter.ColorFormatter(
                        fmt=("[%(levelname)s] [%(asctime)s] %(message)s")
                    )
                ),
            )
        daiquiri.setup(
            level=logging.INFO,
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
