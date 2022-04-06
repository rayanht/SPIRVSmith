import inspect
from types import NoneType
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Callable, Dict, Iterable, Optional, List
from monitor import Event, Monitor
from src.enums import ExecutionModel, StorageClass
from src import Statement, Untyped
from src import predicates
from src.constants import Constant
import random
from src.types.abstract_types import ArithmeticType, ScalarType, Type
from src.types.concrete_types import (
    OpTypeBool,
    OpTypeFunction,
    OpTypeInt,
    OpTypePointer,
    OpTypeVector,
    OpTypeVoid,
)
from src.predicates import (
    HasValidBaseType,
    HasValidBaseTypeAndSign,
    HaveSameTypeLength,
    IsValidBitwiseOperand,
    IsValidLogicalOperand,
)
from src.function import OpFunction

if TYPE_CHECKING:
    from src import OpCode
    from run import SPIRVSmithConfig
from src.memory import OpVariable


class Context:
    id: UUID
    symbol_table: Dict["OpCode", str]
    function: Optional["OpFunction"]
    parent_context: Optional["Context"]
    tvc: Dict["OpCode", str]
    execution_model: ExecutionModel
    config: "SPIRVSmithConfig"
    monitor: Monitor

    def __init__(
        self,
        function: Optional["OpFunction"],
        parent_context: Optional["Context"],
        execution_model: ExecutionModel,
        config: "SPIRVSmithConfig",
        monitor: Monitor,
    ) -> None:
        self.id = uuid4()
        self.symbol_table = dict()
        self.function = function
        self.parent_context = parent_context
        self.execution_model = execution_model
        self.tvc = dict()
        self.config = config
        self.monitor = monitor

    def __eq__(self, other):
        if type(other) is type(self):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)

    def __str__(self) -> str:
        return f"<Context id={self.id} fn={self.function}>"

    @classmethod
    def create_global_context(
        cls,
        execution_model: ExecutionModel,
        config: "SPIRVSmithConfig",
        monitor: Monitor,
    ) -> "Context":
        context = cls(None, None, execution_model, config, monitor)
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
            context = Context(
                function, self, self.execution_model, self.config, self.monitor
            )
        else:
            context = Context(
                self.function, self, self.execution_model, self.config, self.monitor
            )
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

    def get_statements(self, predicate: Callable[[Statement], bool]) -> List[Statement]:
        statements: List[Statement] = list(
            filter(lambda sym: isinstance(sym, Statement), self.symbol_table)
        )
        parent: Optional[Context] = self.parent_context
        while parent:
            statements += list(
                filter(lambda sym: isinstance(sym, Statement), parent.symbol_table)
            )
            parent = parent.parent_context
        return list(filter(predicate, statements))

    def get_typed_statements(
        self, predicate: Optional[Callable[[Statement], bool]] = None
    ) -> List[Statement]:
        statements = self.get_statements(lambda sym: not isinstance(sym, Untyped))
        if not predicate:
            return list(statements)
        return list(filter(predicate, statements))

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

    def get_constants(
        self, predicate: Optional[Callable[[Statement], bool]] = None
    ) -> List[Constant]:
        constants: Iterable[Constant] = filter(
            lambda t: isinstance(t, Constant), self.tvc.keys()
        )
        if not predicate:
            return list(constants)
        return list(filter(predicate, constants))

    def get_random_operand(
        self,
        predicate: Callable[[Statement], bool],
        constraint: Optional[Statement | Constant] = None,
    ) -> Optional[Statement | Constant]:
        statements: list[Statement] = self.get_typed_statements(predicate)
        constants: list[Constant] = self.get_constants(predicate)
        if inspect.stack()[1][0].f_locals["self"].__class__.__name__ == "OpSNegate":
            print(statements)
            print(constants)
            print(self.get_constants())
            exit(0)
        if constraint:
            statements = filter(
                lambda sym: isinstance(sym.type, constraint.type.__class__),
                statements,
            )
            constants = filter(
                lambda const: isinstance(const.type, constraint.type.__class__),
                constants,
            )
            if isinstance(constraint.type, OpTypeVector):
                type_length_predicate = lambda x: HaveSameTypeLength(constraint, x)
                statements = filter(type_length_predicate, statements)
                constants = filter(type_length_predicate, constants)

        statements: list[Statement] = sorted(
            statements, key=lambda sym: sym.id, reverse=True
        )
        # TODO parametrize using a geometric distribution
        try:
            return random.SystemRandom().choice(list(statements) + list(constants))
        except IndexError:
            self.monitor.warning(
                event=Event.NO_OPERAND_FOUND,
                extra={
                    "opcode": inspect.stack()[1][0].f_locals["self"].__class__.__name__,
                    "constraint": str(constraint),
                    "constants": self.get_constants(),
                    "statements": self.get_typed_statements(),
                },
            )
            return None

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
        return (
            self.execution_model == ExecutionModel.GLCompute
            or self.execution_model == ExecutionModel.Kernel
        )
