import random
import subprocess
import tempfile
from dataclasses import field
from enum import Enum

from shortuuid import uuid
from spirv_enums import Decoration
from typing_extensions import Self

from src import OpCode
from src.annotations import OpDecorate
from src.context import Context
from src.misc import OpCapability
from src.misc import OpEntryPoint
from src.misc import OpExecutionMode
from src.misc import OpMemoryModel
from src.monitor import Event
from src.monitor import Monitor
from src.operators.memory.variable import OpVariable
from src.patched_dataclass import dataclass
from src.recondition import recondition_opcodes
from src.types.concrete_types import OpTypeFloat
from src.types.concrete_types import OpTypeInt
from src.utils import get_spirvsmith_version
from src.utils import SubprocessResult
from src.utils import TARGET_SPIRV_VERSION


@dataclass
class SPIRVShader:
    id: str = field(default_factory=lambda: str(uuid()), init=False)
    capabilities: list[OpCapability]
    memory_model: OpMemoryModel
    entry_point: OpEntryPoint
    execution_mode: OpExecutionMode
    opcodes: list[OpCode]
    context: Context

    def generate_assembly_lines(self: Self) -> list[str]:
        assembly_lines: list[str] = [
            "; Magic:     0x07230203 (SPIR-V)",
            f"; Version:   0x00010300 (Version: {get_spirvsmith_version()[1:]})",
            "; Generator: 0x00220001 (SPIRVSmith)",
            f"; Bound:     {len(self.opcodes) + len(self.context.globals) - 1}",
            "; Schema:    0",
        ]
        assembly_lines += [
            capability.to_spasm(self.context) for capability in self.capabilities
        ]
        assembly_lines += [
            ext.to_spasm(self.context) for ext in self.context.extension_sets.values()
        ]
        assembly_lines.append(self.memory_model.to_spasm(self.context))
        assembly_lines.append(self.entry_point.to_spasm(self.context))
        assembly_lines.append(self.execution_mode.to_spasm(self.context))
        assembly_lines += [
            annotation.to_spasm(self.context)
            for annotation in self.context.get_global_context().annotations.keys()
        ]
        assembly_lines += [
            tvc.to_spasm(self.context) for tvc, _ in self.context.globals.items()
        ]
        assembly_lines += [opcode.to_spasm(self.context) for opcode in self.opcodes]
        return assembly_lines

    def generate_assembly_file(self, outfile_path: str) -> None:
        with open(outfile_path, "w") as f:
            f.write("\n".join(self.generate_assembly_lines()))

    def normalise_ids(self: Self) -> Self:
        def id_generator(i=1):
            while True:
                yield i
                i += 1

        id_gen = id_generator()
        for ext in self.context.extension_sets.values():
            ext.id = str(next(id_gen))
        new_tvc = {}
        for tvc in self.context.globals.keys():
            tvc.id = str(next(id_gen))
            new_tvc[tvc] = tvc.id
        self.context.globals = new_tvc
        for opcode in self.opcodes:
            opcode.id = str(next(id_gen))

        return self

    def recondition(self: Self) -> Self:
        self.opcodes = recondition_opcodes(self.context, self.opcodes)
        return self

    def assemble(self: Self, outfile_path: str, silent: bool = False) -> bool:
        with tempfile.NamedTemporaryFile(suffix=".spasm") as spasm_file:
            self.generate_assembly_file(spasm_file.name)
            process_result: SubprocessResult = assemble_spasm_file(
                spasm_file.name, outfile_path
            )
            if process_result.exit_code != 0 and not silent:
                Monitor(self.context.config).error(
                    event=Event.ASSEMBLER_FAILURE,
                    extra={
                        "stderr": process_result.stderr,
                        "executed_command": process_result.executed_command,
                        "shader_id": self.id,
                    },
                )
                return False
            elif not silent:
                Monitor(self.context.config).info(
                    event=Event.ASSEMBLER_SUCCESS, extra={"shader_id": self.id}
                )
                return True

    def validate(self: Self, silent: bool = False) -> bool:
        with tempfile.NamedTemporaryFile(suffix=".spv") as spv_file:
            if not self.assemble(spv_file.name, silent):
                return False
            process_result: SubprocessResult = validate_spv_file(spv_file.name)
            if process_result.exit_code != 0 and not silent:
                Monitor(self.context.config).error(
                    event=Event.VALIDATOR_FAILURE,
                    extra={
                        "stderr": process_result.stderr,
                        "executed_command": process_result.executed_command,
                        "shader_id": self.id,
                    },
                )
                return False
            elif not silent:
                Monitor(self.context.config).info(
                    event=Event.VALIDATOR_SUCCESS,
                    extra={"shader_id": self.id},
                )
                return True


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


def assemble_spasm_file(infile_path: str, outfile_path: str) -> SubprocessResult:
    process: subprocess.CompletedProcess = subprocess.run(
        [
            "spirv-as",
            "--target-env",
            TARGET_SPIRV_VERSION,
            infile_path,
            "-o",
            outfile_path,
        ],
        capture_output=True,
    )
    return SubprocessResult(
        process.returncode,
        process.stdout.decode("utf-8"),
        process.stderr.decode("utf-8"),
        " ".join(process.args),
    )


def disassemble_spv_file(spv_path: str, outfile_path: str, silent: bool = False):
    process: subprocess.CompletedProcess = subprocess.run(
        [
            "spirv-dis",
            "--no-indent",
            "--raw-id",
            "-o",
            outfile_path,
            spv_path,
        ],
        capture_output=True,
    )
    if process.returncode != 0 and not silent:
        Monitor().error(
            event=Event.DISASSEMBLER_FAILURE,
            extra={
                "stderr": process.stderr.decode("utf-8"),
                "run_args": " ".join(process.args),
                "shader_id": spv_path.split("/")[-1].split(".spv")[0],
            },
        )
    elif not silent:
        Monitor().info(
            event=Event.DISASSEMBLER_SUCCESS,
            extra={"shader_id": spv_path.split("/")[-1].split(".spv")[0]},
        )

    return process.returncode == 0


def validate_spv_file(
    filename: str,
) -> SubprocessResult:
    process: subprocess.CompletedProcess = subprocess.run(
        [
            "spirv-val",
            "--target-env",
            TARGET_SPIRV_VERSION,
            filename,
        ],
        capture_output=True,
    )
    return SubprocessResult(
        process.returncode,
        process.stdout.decode("utf-8"),
        process.stderr.decode("utf-8"),
        " ".join(process.args),
    )


def optimise_spv_file(shader: SPIRVShader, filename: str) -> bool:
    process: subprocess.CompletedProcess = subprocess.run(
        [
            shader.context.config.binaries.OPTIMISER_PATH,
            f"--target-env={TARGET_SPIRV_VERSION}",
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
                "run_args": " ".join(process.args),
                "shader_id": shader.id,
            },
        )
    else:
        Monitor(shader.context.config).info(
            event=Event.OPTIMIZER_SUCCESS, extra={"shader_id": shader.id}
        )

    return process.returncode == 0


def reduce_spv_file(shader: SPIRVShader, filename: str) -> bool:
    process: subprocess.CompletedProcess = subprocess.run(
        [
            shader.context.config.binaries.OPTIMISER_PATH,
            f"--target-env={TARGET_SPIRV_VERSION}",
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
                "run_args": " ".join(process.args),
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
    shader_interfaces: list[OpVariable] = shader.context.get_storage_buffers()
    struct_declarations: list[AmberStructDeclaration] = []
    buffers: list[AmberStructDefinition] = []
    bindings: list[int] = sorted(
        map(
            lambda b: b.extra_operands[0],
            filter(
                lambda a: isinstance(a, OpDecorate)
                and a.decoration == Decoration.Binding,
                list(shader.context.annotations.keys()),
            ),
        )
    )
    random.seed(len(shader.opcodes))
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
        fw.write(
            f"SHADER compute {'shader'} SPIRV-ASM TARGET_ENV {TARGET_SPIRV_VERSION}\n"
        )
        with tempfile.NamedTemporaryFile(suffix=".spasm") as fr:
            shader.generate_assembly_file(fr.name)
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
        for buffer, binding in zip(buffers, bindings):
            fw.write(
                f"BIND BUFFER {buffer.name} AS storage DESCRIPTOR_SET 0 BINDING {binding}\n"
            )
        fw.write("END\n")
        fw.write("RUN pipeline 1 1 1\n")
