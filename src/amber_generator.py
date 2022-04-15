from dataclasses import dataclass
from enum import Enum
import random
from typing import TYPE_CHECKING
from src.monitor import Event, Monitor
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
class AmberStructDefinition:
    name: str
    struct_name: str
    initializers: list[float | int]

    def to_amberscript(self):
        return f"BUFFER {self.name} DATA_TYPE {self.struct_name} STD430 DATA\n{chr(10).join([str(initializer) for initializer in self.initializers])}\nEND"


@dataclass
class AmberStructMember:
    name: str
    type: AmberBufferType
    value: float | int


@dataclass
class AmberStructDeclaration:
    name: str
    members: list[AmberStructMember]
    
    def to_amberscript(self):
        return f"STRUCT {self.name}\n{chr(10).join([f'{member.type.value} {member.name}' for member in self.members])}\nEND"


class AmberGenerator:
    config: "SPIRVSmithConfig"
    monitor: Monitor

    def submit(self, shader: "SPIRVShader"):
        # TODO we assume everything is a struct, relax this assumption at some point in the future
        shader_interfaces: list[OpVariable] = shader.context.get_storage_buffers()
        struct_declarations: list[AmberStructDeclaration] = []
        buffers: list[AmberStructDefinition] = []
        for i, interface in enumerate(shader_interfaces):
            amber_struct_members = []
            for j, member in enumerate(interface.type.type.types):
                match m := member:
                    case OpTypeInt() if m.signed:
                        amber_struct_members.append(
                            AmberStructMember(
                                f"var{j}",
                                AmberBufferType.INT32,
                                random.randint(-64, 64),
                            )
                        )
                    case OpTypeInt():
                        amber_struct_members.append(
                            AmberStructMember(
                                f"var{j}",
                                AmberBufferType.UINT32,
                                random.randint(0, 128),
                            )
                        )
                    case OpTypeFloat():
                        amber_struct_members.append(
                            AmberStructMember(
                                f"var{j}",
                                AmberBufferType.FLOAT,
                                random.uniform(-64, 64),
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
            struct_declarations.append(
                AmberStructDeclaration(f"struct{i}", amber_struct_members)
            )
        for i, declaration in enumerate(struct_declarations):
            buffers.append(
                AmberStructDefinition(
                    f"struct{i}",
                    declaration.name,
                    [member.value for member in declaration.members],
                )
            )
        with open(f"out/{shader.id}/out.amber", "w") as fw:
            fw.write("#!amber\n")
            fw.write(f"SHADER compute {'shader'} SPIRV-ASM TARGET_ENV spv1.3\n")
            with open(f"out/{shader.id}/shader.spasm", "r") as fr:
                lines = fr.readlines()
                for line in lines:
                    fw.write(line)
                fw.write("END\n")
            for struct in struct_declarations:
                fw.write(f"{struct.to_amberscript()}\n")
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
