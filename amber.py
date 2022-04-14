from dataclasses import dataclass
from enum import Enum
import random
import subprocess
from typing import TYPE_CHECKING
from monitor import Event, Monitor
from src.memory import OpVariable
from src.types.concrete_types import OpTypeFloat, OpTypeInt

if TYPE_CHECKING:
    from run_local import SPIRVSmithConfig
    from src.fuzzing_server import SPIRVShader


class AmberBufferType(Enum):
    INT8 = "int8"
    INT16 = "int16"
    INT32 = "int32"
    INT64 = "int64"
    UINT8 = "uint8"
    UINT16 = "uint16"
    UINT32 = "uint32"
    UINT64 = "uint64"
    FLOAT16 = "float16"
    FLOAT = "float"
    DOUBLE = "double"


@dataclass
class AmberBuffer:
    name: str
    type: AmberBufferType
    initializer: float | int

    def to_amberscript(self):
        return f"BUFFER {self.name} DATA_TYPE {self.type.value} STD430 DATA\n{self.initializer}\nEND"


class AmberGenerator:
    config: "SPIRVSmithConfig"
    monitor: Monitor

    def submit(self, shader: "SPIRVShader"):
        shader_interfaces: list[OpVariable] = shader.context.get_storage_buffers()
        buffers: list[AmberBuffer] = []
        for k, interface in enumerate(shader_interfaces):
            match i := interface.type.type:
                case OpTypeInt() if i.signed:
                    buffers.append(
                        AmberBuffer(
                            f"buf{k}", AmberBufferType.INT32, random.randint(-64, 64)
                        )
                    )
                case OpTypeInt():
                    buffers.append(
                        AmberBuffer(
                            f"buf{k}", AmberBufferType.UINT32, random.randint(0, 128)
                        )
                    )
                case OpTypeFloat():
                    buffers.append(
                        AmberBuffer(
                            f"buf{k}", AmberBufferType.FLOAT, random.uniform(0, 128)
                        )
                    )
                case _:
                    self.monitor.error(
                        event=Event.INVALID_TYPE_AMBER_BUFFER,
                        extra={
                            "shader_id": shader.id,
                            "interface": interface,
                            "interface_type": interface.type,
                            "interface_inner_type": interface.type.type,
                        },
                    )
        with open(f"out/{shader.id}/out.amber", "w") as fw:
            fw.write("#!amber\n")
            fw.write(f"SHADER compute {'shader'} SPIRV-ASM TARGET_ENV spv1.3\n")
            with open(f"out/{shader.id}/shader.spasm", "r") as fr:
                lines = fr.readlines()
                for line in lines:
                    fw.write(line)
                fw.write("END\n")
            for buffer in buffers:
                fw.write(f"{buffer.to_amberscript()}\n")
            fw.write(f"PIPELINE {'compute'} pipeline\n")
            fw.write(f"ATTACH {'shader'}\n")
            for i, buffer in enumerate(buffers):
                fw.write(
                    f"BIND BUFFER {buffer.name} AS storage DESCRIPTOR_SET 0 BINDING {i}\n"
                )
            fw.write("END\n")
            fw.write("RUN pipeline 1 1 1\n")
