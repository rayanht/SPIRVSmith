from src import OpCode, OpCode


class OpExtension(OpCode):
    name: str


class OpExtInstImport(OpCode):
    name: str = None


# @dataclass
# class OpExtInst(OpCode):
#     name: str
#     def get_required_capabilities(self) -> List[Capability]:
#         return []
