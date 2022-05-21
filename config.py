import random
from dataclasses import dataclass

from src.utils import get_spirvsmith_version

rng = random.SystemRandom()


@dataclass
class BinariesConfig:
    ASSEMBLER_PATH: str = "bin/spirv-as"
    VALIDATOR_PATH: str = "bin/spirv-val"
    OPTIMISER_PATH: str = "bin/spirv-opt"
    CROSS_PATH: str = "bin/spirv-cross"
    AMBER_PATH: str = "bin/amber"


@dataclass
class MutationsConfig:
    # Operations
    w_memory_operation: tuple[int, int] = (1, 2)
    w_logical_operation: tuple[int, int] = (2, 6)
    w_arithmetic_operation: tuple[int, int] = (2, 6)
    w_control_flow_operation: tuple[int, int] = (0, 2)
    w_function_operation: tuple[int, int] = (1, 1)
    w_bitwise_operation: tuple[int, int] = (2, 6)
    w_conversion_operation: tuple[int, int] = (2, 6)
    w_composite_operation: tuple[int, int] = (2, 6)

    # Types
    w_scalar_type: tuple[int, int] = (1, 3)
    w_container_type: tuple[int, int] = (1, 3)

    # Constants
    w_composite_constant: tuple[int, int] = (1, 3)
    w_scalar_constant: tuple[int, int] = (2, 4)


@dataclass
class LimitsConfig:
    # How many types should the fuzzer aim to generate.
    n_types: int = 20
    # How many constants should the fuzzer aim to generate.
    n_constants: int = 50
    # How many functions should the fuzzer aim to generate.
    n_functions: int = 1
    # How deep can the shader go when generating shaders (in terms of control flow).
    # e.g. with a depth of 2, the fuzzer will never generate a triply-nested loop.
    max_depth: int = 3


@dataclass
class FuzzingStrategyConfig:
    mutations_config: MutationsConfig = MutationsConfig()

    # If True, SPIRVSmith will include instructions from
    # the GLSL extension in generated shaders
    enable_ext_glsl_std_450: bool = True

    # The following parameters are used to determine
    # what instructions will be generated by SPIRVSmith.
    #
    # These are interpreted by the fuzzer as weights rather than probabilities.
    # i.e. if you set:
    #   w_logical_operation = 1
    #   w_arithmetic_operation = 2
    # then the fuzzer will generate twice as many arithmetic operations.
    #
    # Classification of operations:
    #   memory_operations       -> OpLoad, OpStore, OpAccessChain etc.
    #   logical_operations      -> OpLogicalNot, OpLogicalAnd, OpIEqual etc.
    #   arithmetic_operations   -> OpIAdd, OpSMod, OpUDiv etc.
    #       (/!\ all instructions from the GLSL extensions are considered arithmetic /!\)
    #   control_flow_operations -> OpSelectionMerge, OpLoopMerge etc.
    #   function_operations     -> OpFunctionCall, OpReturn etc.
    #   bitwise_operations      -> OpBitwiseAnd, OpBitwiseOr etc.
    #   conversion_operations   -> OpConvertFToU, OpConvertFToS etc.
    #   composite_operations    -> OpVectorExtractDynamic, OpCompositeConstruct etc.
    #
    # If you want to prevent SPIRVSmith from generating any of these operations,
    # simply set the corresponding weight to 0.
    w_memory_operation: int = rng.randint(*mutations_config.w_memory_operation)
    w_logical_operation: int = rng.randint(*mutations_config.w_logical_operation)
    w_arithmetic_operation: int = rng.randint(*mutations_config.w_arithmetic_operation)
    w_control_flow_operation: int = rng.randint(
        *mutations_config.w_control_flow_operation
    )
    w_function_operation: int = rng.randint(*mutations_config.w_function_operation)
    w_bitwise_operation: int = rng.randint(*mutations_config.w_bitwise_operation)
    w_conversion_operation: int = rng.randint(*mutations_config.w_conversion_operation)
    w_composite_operation: int = rng.randint(*mutations_config.w_composite_operation)

    # The following parameters are used to determine
    # what types will be generated by SPIRVSmith
    #
    # They are similarly interpreted as weight rather than probabilities.
    #
    # Classification of types:
    #   scalar_types    -> OpTypeInt, OpTypeFloat, OpTypeBool
    #   container_types -> OpTypeVector, OpTypeMatrix, OpTypeArray etc.
    #
    # In practice, this is only useful when you want to prevent SPIRVSmith
    # from generating container types as there are only a few scalar types
    # that can be generated until we exhaust them all and SPIRVSmith is forced
    # to generate container types to fulfill the quota specified in the LimitsConfig.
    w_scalar_type: int = rng.randint(*mutations_config.w_scalar_type)
    w_container_type: int = rng.randint(*mutations_config.w_container_type)

    # The following parameters are used to determine
    # what constants will be generated by SPIRVSmith
    #
    # They are similarly interpreted as weight rather than probabilities.
    #
    # Classification of types:
    #   scalar_constant    -> OpConstant with underlying type OpTypeInt, OpTypeFloat, OpTypeBool
    #   composite_constant -> OpConstantComposite with underlying type OpTypeVector, OpTypeMatrix etc.
    w_composite_constant: int = rng.randint(*mutations_config.w_composite_constant)
    w_scalar_constant: int = rng.randint(*mutations_config.w_scalar_constant)

    # P(generating a statement at step t + 1 | a statement was generated at step t)
    p_statement: float = 0.995

    # The following parameter is used to determine how much the fuzzer should
    # favour statements rather than constants when looking for operands.
    #
    # When SPIRVSmith has to pick operands for an operation (say an OpIAdd),
    # it has the choice between:
    #   - Constants  -> a global OpConstant or OpConstantComposite
    #   - Statements -> the result of a previous operation in scope
    #
    # Setting a higher probability will favour statements over constants.
    p_picking_statement_operand: float = 0.5

    # The following parameter is used to determine how often a fuzzer mutation
    # should be trigger.
    #
    # When a mutation is triggered, one random parameter from FuzzingStrategyConfig
    # is chosen and slightly altered, within the bounds specified in the MutationsConfig.
    #
    # This is only useful in practice in the context of looking for bugs in
    # consumers of SPIR-V since it increases variance.
    mutation_rate: float = 0.05


@dataclass
class MiscConfig:
    # The following parameters are only useful when running SPIRVSmith in
    # a distributed fashion. Enabling these will almost definitely crash SPIRVSmith
    # unless you have deployed the associated infrastructure and have a credentials file.
    start_web_server: bool = False
    broadcast_generated_shaders: bool = False
    upload_logs: bool = False
    version: str = get_spirvsmith_version()


@dataclass
class SPIRVSmithConfig:
    # Binaries
    binaries: BinariesConfig = BinariesConfig()

    # Limits
    limits: LimitsConfig = LimitsConfig()

    # Fuzzing strategy
    strategy: FuzzingStrategyConfig = FuzzingStrategyConfig()

    # Misc
    misc: MiscConfig = MiscConfig()
