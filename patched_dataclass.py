from dataclasses import dataclass


dataclass = dataclass(
    init=True, repr=False, eq=False, order=False, unsafe_hash=False, frozen=False
)
