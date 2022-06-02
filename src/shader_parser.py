from dataclasses import fields
from inspect import isclass
from typing import Optional

from spirv_enums import AddressingModel
from spirv_enums import Capability
from spirv_enums import ExecutionModel
from spirv_enums import MemoryModel
from spirv_enums import SPIRVEnum

from src import OpCode
from src.context import Context
from src.misc import OpCapability
from src.misc import OpEntryPoint
from src.misc import OpExecutionMode
from src.misc import OpMemoryModel
from src.shader_utils import SPIRVShader
from src.types.concrete_types import EmptyType
from src.utils import CLASSES


def attempt_numeric_coercion(string: str) -> int | float | str:
    if string.isnumeric() or string.replace("-", "").isnumeric():
        return int(string)
    try:
        val = float(string)
        return val
    except (TypeError, ValueError):
        return string


def resolve_operands(
    opcode_class: type[OpCode],
    operands: list[str],
    opcode_lookup_table: dict[str, OpCode],
) -> tuple[OpCode | str | int | float, ...]:
    resolved_operands: list[OpCode | str | int | float] = []
    enum_idx: int = 0
    for operand in operands:
        if operand.startswith("%"):
            resolved_operands.append(opcode_lookup_table[operand])
        else:
            resolved_operand: int | float | str = attempt_numeric_coercion(operand)
            if isinstance(resolved_operand, str):
                try:
                    resolved_operand: OpCode = CLASSES[operand]
                except KeyError:
                    enums: list[type[SPIRVEnum]] = [
                        x.type
                        for x in fields(opcode_class)
                        if isclass(x.type) and issubclass(x.type, SPIRVEnum)
                    ][enum_idx:]
                    if enums:
                        enum_class: type[SPIRVEnum] = enums[0]
                        try:
                            if resolved_operand == "None":
                                resolved_operand = "NONE"
                            resolved_operand = enum_class(resolved_operand)
                        except ValueError:
                            pass
                        else:
                            enum_idx += 1
                    else:
                        resolved_operand = resolved_operand.replace('"', "")
            resolved_operands.append(resolved_operand)
    typed_operands: tuple[OpCode] = tuple(resolved_operands)
    if opcode_class.__name__ == "OpTypeStruct":
        typed_operands = (typed_operands,)
    if opcode_class.__name__ == "OpReturn":
        typed_operands = (EmptyType(),)
    if opcode_class.__name__ in {"OpStore", "OpSelectionMerge", "OpLoopMerge"}:
        typed_operands = (EmptyType(), *typed_operands)
    elif opcode_class.__name__ == "OpConstantComposite":
        typed_operands = (typed_operands[0], typed_operands[1:])
    elif opcode_class.__name__ in {
        "OpCompositeExtract",
        "OpExecutionMode",
        "OpAccessChain",
        "OpInBoundsAccessChain",
        "OpDecorate",
    }:
        typed_operands = (*typed_operands[:2], typed_operands[2:])
    elif opcode_class.__name__ in {
        "OpExtInst",
        "OpVectorShuffle",
        "OpCompositeInsert",
        "OpEntryPoint",
        "OpMemberDecorate",
    }:
        typed_operands = (*typed_operands[:3], typed_operands[3:])
    return typed_operands


def parse_spirv_assembly_lines(lines: list[str]) -> SPIRVShader:
    capabilities: list[OpCapability] = []
    global_context: Context = Context.create_global_context(
        ExecutionModel.GLCompute, None
    )
    current_context = global_context
    deferred_lines: list[list[str]] = []
    deferred_indices: list[tuple[int, list[str]]] = []
    opcode_lookup_table: dict[str, OpCode] = {}
    opcodes: list[OpCode] = []
    current_opcode: Optional[OpCode] = None
    for line in (line.split(" ") for line in lines):
        match line:
            case [";", *_]:
                continue
            case ["OpCapability", capability]:
                capabilities.append(OpCapability(Capability(capability)))
            case ["OpMemoryModel", addressing_model, memory_model]:
                memory_model: OpMemoryModel = OpMemoryModel(
                    AddressingModel(addressing_model), MemoryModel(memory_model)
                )
            case [
                "OpEntryPoint" | "OpExecutionMode" | "OpDecorate" | "OpMemberDecorate",
                *_,
            ]:
                deferred_lines.append(line)
            case [
                "OpSelectionMerge" | "OpLoopMerge" | "OpBranch" | "OpBranchConditional",
                *operands,
            ]:
                opcode_class: type[OpCode] = CLASSES[line[0]]
                opcodes.append(opcode_class)
                deferred_indices.append((len(opcodes) - 1, operands))
                current_opcode = None
                continue
            case [opcode_id, "=", opcode_name, *operands]:
                opcode_class: type[OpCode] = CLASSES[opcode_name]
                resolved_operands: tuple[OpCode] = resolve_operands(
                    opcode_class, operands, opcode_lookup_table
                )
                current_opcode = opcode_class(*resolved_operands)
                current_opcode.id = opcode_id.replace("%", "")
                opcode_lookup_table[opcode_id] = current_opcode
            case [opcode_name, *operands]:
                opcode_class: type[OpCode] = CLASSES[opcode_name]
                resolved_operands: tuple[OpCode] = resolve_operands(
                    opcode_class, operands, opcode_lookup_table
                )
                current_opcode = opcode_class(*resolved_operands)
        if current_opcode is not None:
            # Massive hacks ahead to avoid the double import trap
            if current_opcode.__class__.__name__.startswith(
                ("OpType", "OpConstant", "OpVariable")
            ):
                current_context.add_to_tvc(current_opcode)
            elif current_opcode.__class__.__name__ in {
                "OpExtInstImport",
                "OpExtension",
            }:
                current_context.extension_sets[current_opcode.name] = current_opcode
            else:
                current_context.symbol_table.append(current_opcode)
                if current_opcode.__class__.__name__ == "OpFunction":
                    current_context = current_context.make_child_context(current_opcode)
                    current_context.current_function_type = current_opcode.function_type
                opcodes.append(current_opcode)
            current_opcode = None
    for [opcode_name, *operands] in deferred_lines:
        opcode_class: type[OpCode] = CLASSES[opcode_name]
        resolved_operands: tuple[OpCode] = resolve_operands(
            opcode_class, operands, opcode_lookup_table
        )
        opcode: OpCode = opcode_class(*resolved_operands)
        if opcode_name in {"OpDecorate", "OpMemberDecorate"}:
            current_context.add_annotation(opcode)
        elif opcode_name == "OpEntryPoint":
            entry_point: OpEntryPoint = opcode
        elif opcode_name == "OpExecutionMode":
            execution_mode: OpExecutionMode = opcode
    for idx, operands in deferred_indices:
        resolved_operands: tuple[OpCode] = resolve_operands(
            opcodes[idx], operands, opcode_lookup_table
        )
        opcodes[idx] = opcodes[idx](*resolved_operands)
    return SPIRVShader(
        capabilities=capabilities,
        memory_model=memory_model,
        entry_point=entry_point,
        execution_mode=execution_mode,
        opcodes=opcodes,
        context=current_context.get_global_context(),
    )


def parse_spirv_assembly_file(filename: str) -> SPIRVShader:
    with open(filename, "r") as fr:
        lines: list[list[str]] = list(map(lambda l: l.strip(), fr.readlines()))
    return parse_spirv_assembly_lines(lines)
