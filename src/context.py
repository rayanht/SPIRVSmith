import inspect
import random
from dataclasses import dataclass
from dataclasses import field
from types import NoneType
from typing import Callable
from typing import Iterable
from typing import Optional
from typing import TYPE_CHECKING

import ulid
from typing_extensions import Self

from src import AbortFuzzing
from src import FuzzResult
from src import Statement
from src import Untyped
from src.annotations import Annotation
from src.annotations import OpDecorate
from src.annotations import OpMemberDecorate
from src.constants import CompositeConstant
from src.constants import Constant
from src.constants import OpConstant
from src.constants import OpConstantComposite
from src.constants import ScalarConstant
from src.enums import Decoration
from src.enums import ExecutionModel
from src.enums import StorageClass
from src.function import OpFunction
from src.monitor import Event
from src.monitor import Monitor
from src.operators import Operand
from src.predicates import (
    HaveSameTypeLength,
)
from src.types.abstract_types import Type
from src.types.concrete_types import OpTypeFunction
from src.types.concrete_types import OpTypePointer
from src.types.concrete_types import OpTypeStruct
from src.types.concrete_types import OpTypeVector

if TYPE_CHECKING:
    from src import OpCode
    from src.extension import OpExtInstImport
    from run import SPIRVSmithConfig
from src.operators.memory.memory_access import OpVariable


@dataclass
class Context:
    id: str = field(default_factory=lambda: ulid.new().str, init=False)
    function: Optional["OpFunction"]
    parent_context: Optional["Context"]
    execution_model: ExecutionModel
    config: "SPIRVSmithConfig"
    rng: random.SystemRandom
    symbol_table: list["OpCode"] = field(default_factory=list)
    tvc: dict["OpCode", str] = field(default_factory=dict)
    annotations: dict[Annotation, NoneType] = field(default_factory=dict)
    extension_sets: dict[str, "OpExtInstImport"] = field(default_factory=dict)

    @classmethod
    def create_global_context(
        cls,
        execution_model: ExecutionModel,
        config: "SPIRVSmithConfig",
    ) -> "Context":
        return cls(None, None, execution_model, config, random.SystemRandom())

    def make_child_context(self, function: Optional[OpFunction] = None) -> Self:
        return Context(
            function if function else self.function,
            self,
            self.execution_model,
            self.config,
            self.rng,
            tvc=self.tvc,
            annotations=self.annotations,
            extension_sets=self.extension_sets,
        )

    def add_to_tvc(self, opcode: "OpCode") -> None:
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
            return self.rng.choice(variables)
        except IndexError:
            Monitor(self.config).info(
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
        for _ in range(self.config.limits.n_types - 1):
            try:
                fuzzed_type: FuzzResult = Type.fuzz(self)
            except (RecursionError, AbortFuzzing):
                continue
            for side_effect in fuzzed_type.side_effects:
                self.add_to_tvc(side_effect)
            self.add_to_tvc(fuzzed_type.opcode)
        # We should ALWAYS have at least 1 struct type
        struct_type: FuzzResult = OpTypeStruct.fuzz(self)
        for side_effect in struct_type.side_effects:
            self.add_to_tvc(side_effect)
        self.add_to_tvc(struct_type.opcode)

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
                fuzzed_constant: FuzzResult = ScalarConstant.fuzz(self)
            except (RecursionError, AbortFuzzing):
                continue
            for side_effect in fuzzed_constant.side_effects:
                self.add_to_tvc(side_effect)
            self.add_to_tvc(fuzzed_constant.opcode)
        for _ in range(n_constants - n_scalars):
            try:
                fuzzed_constant: FuzzResult = CompositeConstant.fuzz(self)
            except (RecursionError, AbortFuzzing):
                continue
            for side_effect in fuzzed_constant.side_effects:
                self.add_to_tvc(side_effect)
            self.add_to_tvc(fuzzed_constant.opcode)

    def gen_global_variables(self):
        n = len(self.tvc)
        for i in range(self.rng.randint(1, 3)):
            variable = self.create_on_demand_variable(StorageClass.StorageBuffer)
            if len(self.tvc) != n:
                self.add_annotation(
                    OpDecorate(target=variable.type.type, decoration=Decoration.Block)
                )
                self.add_annotation(
                    OpDecorate(
                        target=variable,
                        decoration=Decoration.DescriptorSet,
                        extra_operands=(0,),
                    )
                )
                self.add_annotation(
                    OpDecorate(
                        target=variable,
                        decoration=Decoration.Binding,
                        extra_operands=(i,),
                    )
                )
                offset = 0
                for j, t in enumerate(variable.type.type.types):
                    self.add_annotation(
                        OpMemberDecorate(
                            target_struct=variable.type.type,
                            member=j,
                            decoration=Decoration.Offset,
                            extra_operands=(offset,),
                        )
                    )
                    offset += t.width
            n = len(self.tvc)

    def gen_opcodes(self) -> list["OpCode"]:
        function_types: list[OpTypeFunction] = self.get_function_types()
        function_bodies: list["OpCode"] = []
        functions: list[OpFunction] = []

        for function_type in function_types:
            self.current_function_type = function_type
            fuzzed_function: FuzzResult = OpFunction.fuzz(self)
            if function_type == self.main_type:
                self.main_fn = fuzzed_function.opcode
            functions.append(fuzzed_function.opcode)
            function_bodies.append(fuzzed_function.opcode)
            function_bodies += fuzzed_function.side_effects
        return function_bodies

    def get_constants(
        self, predicate: Optional[Callable[[Constant], bool]] = None
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
    ) -> Operand:
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

        # TODO parametrize using a geometric distribution
        try:
            if (
                self.rng.random() < self.config.strategy.p_picking_statement_operand
                and len(list(statements)) > 0
            ):
                potential_operands: list[Statement] = list(statements)
                weights = [
                    len(potential_operands) - n + len(potential_operands) // 2
                    for n in range(len(potential_operands))
                ]
                try:
                    return self.rng.choices(potential_operands, weights=weights, k=1)[0]
                except IndexError:
                    return self.rng.choice(list(constants))
            else:
                try:
                    return self.rng.choice(list(constants))
                except IndexError:
                    return self.rng.choice(list(statements))
        except IndexError:
            try:
                opcode_name: str = inspect.stack()[1][0].f_locals["cls"].__name__
            except KeyError:
                try:
                    opcode_name: str = (
                        inspect.stack()[1][0].f_locals["self"].__class__.__name__
                    )
                except KeyError:
                    opcode_name = "unknown"
            Monitor(self.config).info(
                event=Event.NO_OPERAND_FOUND,
                extra={
                    "opcode": opcode_name,
                    "constraint": str(constraint),
                    "constants": self.get_constants(),
                    "statements": self.get_typed_statements(),
                },
            )
            raise AbortFuzzing

    def get_function_types(self) -> list[OpTypeFunction]:
        return list(filter(lambda t: isinstance(t, OpTypeFunction), self.tvc.keys()))

    def get_interfaces(self) -> tuple[OpVariable, ...]:
        return tuple(
            filter(
                lambda s: isinstance(s, OpVariable)
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
        target_type: type[Type],
        value: int = 0,
        width: int = 32,
        signed: Optional[int] = 0,
    ) -> OpConstant:
        constant_type = target_type.fuzz(self).opcode
        constant_type.width = width
        if hasattr(constant_type, "signed"):
            constant_type.signed = signed
        constant = OpConstant(type=constant_type, value=value)
        self.add_to_tvc(constant_type)
        self.add_to_tvc(constant)
        return constant

    def create_on_demand_variable(
        self,
        storage_class: StorageClass,
        type: Optional[Type] = None,
    ):
        if type:
            pointer_inner_type = type
        else:
            pointer_inner_type = self.rng.choice(
                list(
                    filter(
                        lambda tvc: isinstance(tvc, OpTypeStruct),
                        self.tvc.keys(),
                    )
                )
            )
        pointer_type = OpTypePointer(
            storage_class=storage_class, type=pointer_inner_type
        )
        variable: OpVariable = OpVariable(
            type=pointer_type, storage_class=storage_class
        )
        self.add_to_tvc(pointer_type)
        if storage_class != StorageClass.Function:
            self.add_to_tvc(variable)
        return variable

    def create_on_demand_vector_constant(
        self, inner_constant: OpConstant, size: int = 4
    ) -> OpConstantComposite:
        vector_type = OpTypeVector(inner_constant.type, size)
        vector_const = OpConstantComposite(vector_type, tuple([inner_constant] * size))

        self.add_to_tvc(vector_type)
        self.add_to_tvc(vector_const)
        return vector_const

    def get_global_context(self) -> Self:
        current_context = self
        while current_context.parent_context:
            current_context = self.parent_context
        return current_context

    def add_annotation(self, annotation: Annotation):
        self.get_global_context().annotations[annotation] = None
