from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Dict, Optional, List
from langspec.enums import ExecutionModel, StorageClass
from langspec.opcodes import Statement, Untyped
from langspec.opcodes.constants import Constant
import random
from langspec.opcodes.types.abstract_types import ArithmeticType, ScalarType, Type
from langspec.opcodes.types.concrete_types import (
    OpTypeBool,
    OpTypeFunction,
    OpTypePointer,
    OpTypeVoid,
)

from langspec.opcodes.function import OpFunction

if TYPE_CHECKING:
    from langspec.opcodes import OpCode
    from run import SPIRVSmithConfig
from langspec.opcodes.memory import OpVariable


class Context:
    id: UUID
    symbol_table: Dict["OpCode", str]
    function: Optional["OpFunction"]
    parent_context: Optional["Context"]
    tvc: Dict["OpCode", str]
    execution_model: ExecutionModel
    config: "SPIRVSmithConfig"

    def __init__(
        self, function: Optional["OpFunction"], parent_context: Optional["Context"], execution_model: ExecutionModel, config: "SPIRVSmithConfig"
    ) -> None:
        self.id = uuid4()
        self.symbol_table = dict()
        self.function = function
        self.parent_context = parent_context
        self.execution_model = execution_model
        self.tvc = dict()
        self.config = config

    def __eq__(self, other):
        if type(other) is type(self):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)

    def __str__(self) -> str:
        return f"<Context id={self.id} fn={self.function}>"

    @classmethod
    def create_global_context(cls, execution_model: ExecutionModel, config: "SPIRVSmithConfig") -> "Context":
        context = cls(None, None, execution_model, config)
        void_type = OpTypeVoid()
        main_type = OpTypeFunction()
        main_type.return_type = void_type
        main_type.parameter_types = ()
        cls.main_type = main_type
        context.tvc[void_type] = void_type.id
        context.tvc[main_type] = main_type.id
        context.config = config
        return context

    def make_child_context(self, function: OpTypeFunction = None):
        if function:
            context = Context(function, self, self.execution_model, self.config)
        else:
            context = Context(self.function, self, self.execution_model, self.config)
        context.tvc = self.tvc
        return context

    def get_local_variables(self) -> List[OpVariable]:
        variables: List[OpVariable] = list(
            filter(lambda sym: isinstance(sym, OpVariable), self.symbol_table)
        )
        if self.parent_context:
            return variables + self.parent_context.get_local_variables()
        return variables

    def get_global_variables(self) -> List[OpVariable]:
        return list(filter(lambda tvc: isinstance(tvc, OpVariable), self.tvc.keys()))

    def get_statements(self, filter_fn) -> List[Statement]:
        statements: List[Statement] = list(
            filter(lambda sym: isinstance(sym, Statement), self.symbol_table)
        )
        parent: Optional[Context] = self.parent_context
        while parent:
            statements += list(
                filter(lambda sym: isinstance(sym, Statement), parent.symbol_table)
            )
            parent = parent.parent_context
        return list(filter(filter_fn, statements))

    def get_arithmetic_statements(self) -> List[Statement]:
        return self.get_statements(
            lambda sym: not isinstance(sym, Untyped)
            and isinstance(sym.type, ArithmeticType)
        )

    def get_depth(self) -> int:
        depth = 1
        parent: Optional[Context] = self.parent_context
        while parent:
            depth += 1
            parent = parent.parent_context
        return depth

    def gen_types(self):
        for _ in range(self.config.n_types):
            try:
                opcodes: List["OpCode"] = Type().fuzz(self)
            except RecursionError:
                continue
            for opcode in opcodes:
                if opcode not in self.tvc:
                    self.tvc[opcode] = opcode.id

    def gen_constants(self):
        for _ in range(self.config.n_constants):
            try:
                opcodes: List["OpCode"] = Constant().fuzz(self)
            except RecursionError:
                continue
            for opcode in opcodes:
                if opcode not in self.tvc:
                    self.tvc[opcode] = opcode.id

    def gen_variables(self):
        for _ in range(random.randint(1, 3)):
            opcodes: List["OpCode"] = OpVariable().fuzz(self)
            for opcode in opcodes:
                self.tvc[opcode] = opcode.id
        # Generate output
        if self.execution_model != ExecutionModel.GLCompute:
            output: OpVariable = OpVariable()
            output.storage_class = StorageClass.StorageBuffer
            output.context = self
            output.type = OpTypePointer()
            output.type.storage_class = StorageClass.StorageBuffer
            output.type.type = random.choice(
                list(
                    filter(
                        lambda tvc: isinstance(tvc, ScalarType)
                        and not isinstance(tvc, OpTypeBool),
                        self.tvc.keys(),
                    )
                )
            )
            self.tvc[output.type] = output.type.id
            self.tvc[output] = output.id

    def gen_program(self) -> List["OpCode"]:
        function_types: List[OpTypeFunction] = self.get_function_types()
        function_bodies: List["OpCode"] = []
        functions: List[OpFunction] = []

        for function_type in function_types:
            function = OpFunction(
                return_type=function_type.return_type,
                function_type=function_type,
            )
            if function_type == self.main_type:
                self.main_fn = function
            functions.append(function)
            function_bodies += function.fuzz(self)
        return function_bodies

    def get_constants(self, type: Optional[Type] = None) -> List[Constant]:
        if type:
            return list(
                filter(
                    lambda const: isinstance(const, Constant)
                    and isinstance(const.type, type),
                    self.tvc.keys(),
                )
            )
        return list(self.tvc.keys())

    def get_arithmetic_constants(self) -> List[Constant]:
        return self.get_constants(ArithmeticType)

    def get_function_types(self) -> List[OpTypeFunction]:
        return list(filter(lambda t: isinstance(t, OpTypeFunction), self.tvc.keys()))

    def get_interfaces(self) -> List[OpVariable]:
        return list(
            filter(
                lambda s: isinstance(s, OpVariable)
                and not s.context.function
                and (
                    s.storage_class == StorageClass.Input
                    or s.storage_class == StorageClass.Output
                ),
                self.tvc,
            )
        )
    
    def is_compute_shader(self) -> bool:
        return self.execution_model == ExecutionModel.GLCompute or self.execution_model == ExecutionModel.Kernel
