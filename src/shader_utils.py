import subprocess
import tempfile
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from random import SystemRandom

from shortuuid import uuid

from src import OpCode
from src.context import Context
from src.enums import (
    StorageClass,
)
from src.misc import OpCapability
from src.misc import OpEntryPoint
from src.misc import OpExecutionMode
from src.misc import OpMemoryModel
from src.monitor import Event
from src.monitor import Monitor
from src.operators.memory.variable import OpVariable
from src.types.concrete_types import OpTypeFloat
from src.types.concrete_types import OpTypeInt


@dataclass
class SPIRVShader:
    capabilities: list[OpCapability]
    # extension: Optional[list[Extension]]
    # ext_inst: list[ExtInstImport]
    memory_model: OpMemoryModel
    entry_point: OpEntryPoint
    execution_mode: OpExecutionMode
    opcodes: list[OpCode]
    context: Context
    id: str = field(default_factory=uuid)

    def export(self, filename: str) -> None:
        # Generate assembly
        with open(filename, "w") as f:
            f.write("; Magic:     0x07230203 (SPIR-V)\n")
            f.write("; Version:   0x00010300 (Version: 1.3.0)\n")
            f.write("; Generator: 0x00220001 (SPIRVSmith)\n")
            f.write(f"; Bound:     {len(self.opcodes) + len(self.context.tvc) - 1}\n")
            f.write("; Schema:    0\n")
            for capability in self.capabilities:
                f.write(capability.to_spasm(self.context))
            for ext in self.context.extension_sets.values():
                f.write(ext.to_spasm(self.context))
            f.write(self.memory_model.to_spasm(self.context))
            f.write(self.entry_point.to_spasm(self.context))
            f.write(self.execution_mode.to_spasm(self.context))
            for annotation in self.context.get_global_context().annotations.keys():
                f.write(annotation.to_spasm(self.context))
            for tvc, _ in self.context.tvc.items():
                if (
                    isinstance(tvc, OpVariable)
                    and tvc.storage_class == StorageClass.Function
                ):
                    continue
                f.write(tvc.to_spasm(self.context))
            for opcode in self.opcodes:
                f.write(opcode.to_spasm(self.context))


# class CrossLanguage(Enum):
#     MSL = "--msl"


# def cross_compile_shader(
#     shader: SPIRVShader, monitor: Monitor, target_language: CrossLanguage
# ):
#     process: subprocess.CompletedProcess = subprocess.run(
#         [
#             shader.context.config.binaries.CROSS_PATH,
#             f"out/{shader.id}/shader.spv",
#         ],
#         capture_output=True,
#     )
#     if process.returncode != 0:
#         monitor.error(
#             event=Event.VALIDATOR_FAILURE,
#             extra={
#                 "stderr": process.stderr.decode("utf-8"),
#                 "cli_args": str(process.args),
#                 "shader_id": shader.id,
#             },
#         )
#     else:
#         monitor.info(event=Event.VALIDATOR_SUCCESS, extra={"shader_id": shader.id})

#     return process.returncode == 0


def assemble_shader(shader: SPIRVShader, filename: str, silent: bool = False) -> bool:
    with tempfile.NamedTemporaryFile(suffix=".spasm") as infile:
        shader.export(filename=infile.name)
        process: subprocess.CompletedProcess = subprocess.run(
            [
                shader.context.config.binaries.ASSEMBLER_PATH,
                "--target-env",
                "spv1.3",
                infile.name,
                "-o",
                filename,
            ],
            capture_output=True,
        )
        if process.returncode != 0 and not silent:
            Monitor(shader.context.config).error(
                event=Event.ASSEMBLER_FAILURE,
                extra={
                    "stderr": process.stderr.decode("utf-8"),
                    "cli_args": str(process.args),
                    "shader_id": shader.id,
                },
            )
        elif not silent:
            Monitor(shader.context.config).info(
                event=Event.ASSEMBLER_SUCCESS, extra={"shader_id": shader.id}
            )

        return process.returncode == 0


def validate_spirv_file(
    shader: SPIRVShader,
    filename: str,
    opt: bool = False,
    silent: bool = False,
) -> bool:
    process: subprocess.CompletedProcess = subprocess.run(
        [
            shader.context.config.binaries.VALIDATOR_PATH,
            "--target-env",
            "vulkan1.2",
            filename,
        ],
        capture_output=True,
    )
    if process.returncode != 0 and not silent:
        Monitor(shader.context.config).error(
            event=Event.VALIDATOR_OPT_FAILURE if opt else Event.VALIDATOR_FAILURE,
            extra={
                "stderr": process.stderr.decode("utf-8"),
                "cli_args": str(process.args),
                "shader_id": shader.id,
            },
        )
    elif not silent:
        Monitor(shader.context.config).info(
            event=Event.VALIDATOR_OPT_SUCCESS if opt else Event.VALIDATOR_SUCCESS,
            extra={"shader_id": shader.id},
        )

    return process.returncode == 0


def optimise_spirv_file(shader: SPIRVShader, filename: str) -> bool:
    process: subprocess.CompletedProcess = subprocess.run(
        [
            shader.context.config.binaries.OPTIMISER_PATH,
            "--target-env=spv1.3",
            filename,
            "-o",
            f"out/{shader.id}/spv_opt/shader.spv",
        ],
        capture_output=True,
    )
    if process.returncode != 0:
        Monitor(shader.context.config).error(
            event=Event.OPTIMIZER_FAILURE,
            extra={
                "stderr": process.stderr.decode("utf-8"),
                "cli_args": str(process.args),
                "shader_id": shader.id,
            },
        )
    else:
        Monitor(shader.context.config).info(
            event=Event.OPTIMIZER_SUCCESS, extra={"shader_id": shader.id}
        )

    return process.returncode == 0


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


def create_amber_file(shader: SPIRVShader, filename: str) -> None:
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
                            SystemRandom().randint(-64, 64),
                        )
                    )
                case OpTypeInt():
                    amber_struct_members.append(
                        AmberStructMember(
                            f"var{j}",
                            AmberBufferType.UINT32,
                            SystemRandom().randint(0, 128),
                        )
                    )
                case OpTypeFloat():
                    amber_struct_members.append(
                        AmberStructMember(
                            f"var{j}",
                            AmberBufferType.FLOAT,
                            SystemRandom().uniform(-64, 64),
                        )
                    )
                case _:
                    Monitor(shader.context.config).error(
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
    with open(filename, "w") as fw:
        fw.write("#!amber\n")
        fw.write(f"SHADER compute {'shader'} SPIRV-ASM TARGET_ENV spv1.3\n")
        with tempfile.NamedTemporaryFile(suffix=".spasm") as fr:
            shader.export(filename=fr.name)
            lines = fr.readlines()
            for line in lines:
                fw.write(line.decode("utf-8"))
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
