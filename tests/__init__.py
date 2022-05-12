import logging
from typing import TYPE_CHECKING

from src import Type
from src.constants import OpConstant
from src.constants import OpConstantComposite

if TYPE_CHECKING:
    from src.context import Context
from src.types.concrete_types import OpTypeVector


logging.disable(logging.CRITICAL)


def create_vector_const(
    context: "Context", inner_type: Type, size: int = 4, value: int = 42
) -> OpConstant:
    const: OpConstant = context.create_on_demand_numerical_constant(
        inner_type, value=value, width=32
    )

    vector_type = OpTypeVector(type=const.type, size=size)
    vector_const = OpConstantComposite(
        type=vector_type, constituents=tuple([const] * size)
    )
    context.add_to_tvc(vector_type)
    context.add_to_tvc(vector_const)
    return vector_const
