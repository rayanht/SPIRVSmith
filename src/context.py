import inspect
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Callable, Iterable, Optional
from src.annotations import Annotation, OpDecorate, OpMemberDecorate
from src.monitor import Event, Monitor
from src.enums import Decoration, ExecutionModel, StorageClass
from src import Statement, Untyped
from src.constants import CompositeConstant, Constant, OpConstant, ScalarConstant
import random
from src.types.abstract_types import Type
from src.types.concrete_types import (
    OpTypeFunction,
    OpTypePointer,
    OpTypeStruct,
    OpTypeVector,
    OpTypeVoid,
)
from src.predicates import (
    HaveSameTypeLength,
)
from src.function import OpFunction

if TYPE_CHECKING:
    from src import OpCode
    from run_local import SPIRVSmithConfig
from src.memory import OpVariable


class Context:
    id: UUID
    symbol_table: dict["OpCode", str]
    function: Optional["OpFunction"]
    parent_context: Optional["Context"]
    tvc: dict["OpCode", str]
    annotations: list[Annotation]
    execution_model: ExecutionModel
    config: "SPIRVSmithConfig"
    monitor: Monitor

    def __init__(
        self,
        function: Optional["OpFunction"],
        parent_context: Optional["Context"],
        annotations: list[Annotation],
        execution_model: ExecutionModel,
        config: "SPIRVSmithConfig",
        monitor: Monitor,
    ) -> None:
        self.id = uuid4()
        self.symbol_table = dict()
        self.function = function
        self.annotations = annotations
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
        context = cls(None, None, [], execution_model, config, monitor)
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
                function,
                self,
                self.annotations,
                self.execution_model,
                self.config,
                self.monitor,
            )
        else:
            context = Context(
                self.function,
                self,
                self.annotations,
                self.execution_model,
                self.config,
                self.monitor,
            )
        context.tvc = self.tvc
        return context

    def add_to_tvc(self, opcode: "OpCode"):
        if not opcode in self.tvc:
            self.tvc[opcode] = opcode.id

    def get_local_variables(self) -> list[OpVariable]:
        variables: list[OpVariable] = list(
            filter(lambda sym: isinstance(sym, OpVariable), self.symbol_table)
        )
        if self.parent_context:
            return variables + self.parent_context.get_local_variables()
        return variables

    def get_global_variables(self) -> list[OpVariable]:
        return list(filter(lambda tvc: isinstance(tvc, OpVariable), self.tvc.keys()))

    def get_random_variable(
        self, predicate: Callable[[OpVariable], bool]
    ) -> Optional[OpVariable]:
        variables = list(
            filter(predicate, self.get_local_variables() + self.get_global_variables())
        )
        try:
            return random.SystemRandom().choice(variables)
        except IndexError:
            self.monitor.warning(
                event=Event.NO_OPERAND_FOUND,
                extra={
                    "opcode": inspect.stack()[1][0].f_locals["self"].__class__.__name__,
                    "local_vars": self.get_local_variables(),
                    "global_vars": self.get_global_variables(),
                },
            )
            return None

    def get_statements(self, predicate: Callable[[Statement], bool]) -> list[Statement]:
        statements: list[Statement] = list(
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
    ) -> list[Statement]:
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
        for _ in range(self.config.limits.n_types):
            try:
                opcodes: list["OpCode"] = Type().fuzz(self)
            except RecursionError:
                continue
            for opcode in opcodes:
                if opcode not in self.tvc:
                    self.tvc[opcode] = opcode.id

    def gen_constants(self):
        n_constants = self.config.limits.n_constants
        n_scalars = (
            self.config.strategy.w_scalar_constant
            * n_constants
            // (
                self.config.strategy.w_composite_constant
                + self.config.strategy.w_scalar_constant
            )
        )
        for _ in range(n_scalars):
            try:
                opcodes: list["OpCode"] = ScalarConstant().fuzz(self)
            except RecursionError:
                continue
            for opcode in opcodes:
                if opcode not in self.tvc:
                    self.tvc[opcode] = opcode.id
        for _ in range(n_constants - n_scalars):
            try:
                opcodes: list["OpCode"] = CompositeConstant().fuzz(self)
            except RecursionError:
                continue
            for opcode in opcodes:
                if opcode not in self.tvc:
                    self.tvc[opcode] = opcode.id

    def gen_global_variables(self):
        n = len(self.tvc)
        for i in range(random.SystemRandom().randint(1, 3)):
            variable = self.create_on_demand_variable(StorageClass.StorageBuffer)
            if len(self.tvc) != n:
                self.add_annotation(
                    OpDecorate(None, variable.type.type, Decoration.Block)
                )
                self.add_annotation(
                    OpDecorate(None, variable, Decoration.DescriptorSet, (0,))
                )
                self.add_annotation(
                    OpDecorate(None, variable, Decoration.Binding, (i,))
                )
                offset = 0
                for j, t in enumerate(variable.type.type.types):
                    self.add_annotation(
                        OpMemberDecorate(
                            None, variable.type.type, j, Decoration.Offset, (offset,)
                        )
                    )
                    offset += t.width
            n = len(self.tvc)

    def gen_program(self) -> list["OpCode"]:
        function_types: list[OpTypeFunction] = self.get_function_types()
        function_bodies: list["OpCode"] = []
        functions: list[OpFunction] = []

        for function_type in function_types:
            function = OpFunction()
            function.return_type = function_type.return_type
            function.function_type = function_type
            if function_type == self.main_type:
                self.main_fn = function
            functions.append(function)
            function_bodies += function.fuzz(self)
        return function_bodies

    def get_constants(
        self, predicate: Optional[Callable[[Statement], bool]] = None
    ) -> list[Constant]:
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

    def get_function_types(self) -> list[OpTypeFunction]:
        return list(filter(lambda t: isinstance(t, OpTypeFunction), self.tvc.keys()))

    def get_interfaces(self) -> list[OpVariable]:
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

    def get_storage_buffers(self) -> list[OpVariable]:
        return list(
            filter(
                lambda s: isinstance(s, OpVariable)
                and not s.context.function
                and (s.storage_class == StorageClass.StorageBuffer),
                self.tvc,
            )
        )

    def is_compute_shader(self) -> bool:
        return (
            self.execution_model == ExecutionModel.GLCompute
            or self.execution_model == ExecutionModel.Kernel
        )

    def create_on_demand_numerical_constant(
        self,
        target_type: Type,
        value: int = 0,
        width: int = 32,
        signed: Optional[int] = 0,
    ) -> OpConstant:
        type = target_type()
        type.width = width
        if hasattr(type, "signed"):
            type.signed = signed
        constant = OpConstant()
        constant.type = type
        constant.value = value
        if constant in self.tvc:
            return constant
        self.add_to_tvc(type)
        self.add_to_tvc(constant)
        return constant

    def create_on_demand_variable(
        self,
        storage_class: StorageClass,
        type: Optional[Type] = None,
    ):
        variable: OpVariable = OpVariable()
        variable.context = self

        pointer_type = OpTypePointer()
        pointer_type.storage_class = storage_class
        if type:
            pointer_type.type = type
        else:
            pointer_type.type = random.SystemRandom().choice(
                list(
                    filter(
                        lambda tvc: isinstance(tvc, OpTypeStruct),
                        self.tvc.keys(),
                    )
                )
            )
        variable.type = pointer_type
        variable.storage_class = storage_class
        self.add_to_tvc(pointer_type)
        if storage_class != StorageClass.Function:
            self.add_to_tvc(variable)
        return variable

    def add_annotation(self, annotation: Annotation):
        self.annotations.append(annotation)
