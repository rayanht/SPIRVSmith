from langspec.opcodes import Type


class ScalarType(Type):
    pass


class NumericalType(Type):
    pass


class ContainerType(Type):
    pass


class UniformContainerType(ContainerType):
    pass


class MixedContainerType(ContainerType):
    pass


class ArithmeticType(Type):
    pass
