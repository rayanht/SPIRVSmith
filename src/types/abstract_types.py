from src import Type


class ScalarType(Type):
    ...


class NumericalType(Type):
    ...


class ContainerType(Type):
    ...


class ArithmeticType(Type):
    ...


# TODO I fucking hate this type, look into reworking the whole type system
class MiscType(Type):
    ...


class UniformContainerType(ContainerType):
    ...


class MixedContainerType(ContainerType):
    ...
