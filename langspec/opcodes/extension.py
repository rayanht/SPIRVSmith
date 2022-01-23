from langspec.opcodes import OpCode, OpCode


class OpExtension(OpCode):
    name: str


class OpExtInstImport(OpCode):
    name: str = None


# @dataclass
# class OpExtInst(OpCode):
#     name: str

#     def validate_opcode(self) -> bool:
#         return True

#     def get_required_capabilities(self) -> List[Capability]:
#         return []
