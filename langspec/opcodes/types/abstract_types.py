from langspec.opcodes import Type


class ScalarType(Type):
    ...


class NumericalType(Type):
    ...


class ContainerType(Type):
    ...


class UniformContainerType(ContainerType):
    ...


class MixedContainerType(ContainerType):
    ...


class ArithmeticType(Type):
    ...
