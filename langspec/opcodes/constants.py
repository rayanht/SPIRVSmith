import random
from typing import TYPE_CHECKING, List, Union

from langspec.opcodes import (
    Constant,
    OpCode,
)

if TYPE_CHECKING:
    from langspec.opcodes.context import Context
from langspec.opcodes.types.abstract_types import (
    NumericalType,
    Type,
)
from langspec.opcodes.types.concrete_types import (
    OpTypeBool,
)
from patched_dataclass import dataclass


class OpConstantTrue(Constant):
    type: Type = None

    def fuzz(self, context: "Context") -> List[OpCode]:
        self.type = OpTypeBool()
        return [self.type, self]


class OpConstantFalse(Constant):
    type: Type = None

    def fuzz(self, context: "Context") -> List[OpCode]:
        self.type = OpTypeBool()
        return [self.type, self]


@dataclass
class OpConstant(Constant):
    type: Type = None
    value: Union[int, float] = None

    def fuzz(self, context: "Context") -> List[OpCode]:

        self.type = NumericalType().fuzz(context)[0]
        from langspec.opcodes.types.concrete_types import OpTypeInt

        if isinstance(self.type, OpTypeInt):
            if self.type.signed:
                self.value = random.randint(
                    -(2 ** (self.type.width - 1)), 2 ** (self.type.width - 1) - 1
                )
            else:
                self.value = random.randint(0, 2 ** self.type.width)
        else:
            self.value = random.uniform(0, 2 ** self.type.width)

        return [self.type, self]


# @dataclass
# class OpConstantComposite(Constant):
#     constants: Tuple[Constant]

#     def fuzz(self,  tvc, context: Context) -> List[OpCode]:
#
#         self.type: Union[MixedContainerType, UniformContainerType] = random.choice(
#             list(
#                 filter(
#                     lambda tvc: isinstance(tvc, ContainerType)
#                     and not isinstance(tvc, OpTypePointer),
#                     TVC_table.keys(),
#                 )
#             )
#         )
#         self.constants = []
#         if isinstance(self.type, UniformContainerType):
#             for _ in range(len(self.type)):
#                 constant: Constant = find_constant(tvc, self.type.type,  context)
#                 self.constants.append(constant)
#         else:
#             for type in self.type.types:
#                 constant: Constant = find_constant(tvc, type,  context)
#                 self.constants.append(constant)
#         self.constants = tuple(self.constants)
#         return [self]

#     def to_spasm(self, TVC_table) -> str:
#         spasm = f"%{self.id} = OpConstantComposite %{TVC_table[self.type]}"
#         for constant in self.constants:
#             spasm += f" %{TVC_table[constant]}"
#         return spasm
