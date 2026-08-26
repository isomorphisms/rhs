"""Minimal boundary for checking whether two sides mean the same thing.

Both sides are produced from exactly one input.  This module deliberately
makes no decision about how to compare them: exact equality, embeddings, or a
vector database can consume the returned observation later.
"""

from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

Input = TypeVar("Input")
Left = TypeVar("Left")
Right = TypeVar("Right")


@dataclass(frozen=True)
class EqualityObservation(Generic[Input, Left, Right]):
    input: Input
    lhs: Left
    rhs: Right


def both_sides(
    value: Input,
    lhs: Callable[[Input], Left],
    rhs: Callable[[Input], Right],
) -> EqualityObservation[Input, Left, Right]:
    """Produce the left- and right-hand sides from the exact same input."""
    return EqualityObservation(
        input=value,
        lhs=lhs(value),
        rhs=rhs(value),
    )
