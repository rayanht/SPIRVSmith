from src import Type


class ScalarType(Type):
    ...


class NumericalType(Type):
    ...


class ContainerType(Type):
    ...


class ArithmeticType(Type):
    ...


class UniformContainerType(ContainerType):
    ...


class MixedContainerType(ContainerType):
    ...
