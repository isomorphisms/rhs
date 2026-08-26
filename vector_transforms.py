#!/usr/bin/env python3
"""Exact orthogonal transforms for LHS/RHS vector verification experiments.

These helpers deliberately avoid arbitrary-angle trigonometry.  Verification
code often wants to compare vectors repeatedly and exactly; quarter turns and
coordinate reflections give useful orientation changes without introducing
cos/sin approximation noise.
"""

from __future__ import annotations

from typing import Sequence


def _checked_vector(vector: Sequence[float]) -> tuple[float, ...]:
    checked = tuple(float(value) for value in vector)
    if not checked:
        raise ValueError("vector must contain at least one coordinate")
    return checked


def _checked_coordinate(coordinate: int, dimensions: int, label: str) -> int:
    if isinstance(coordinate, bool) or not isinstance(coordinate, int):
        raise TypeError(f"{label} must be an integer coordinate index")
    if coordinate < 0 or coordinate >= dimensions:
        raise IndexError(f"{label} is outside vector dimensions")
    return coordinate


def reflect_coordinate(vector: Sequence[float], coordinate: int) -> tuple[float, ...]:
    """Reflect a vector through the coordinate hyperplane x_coordinate = 0.

    Equivalently, negate exactly one coordinate and leave every other
    coordinate unchanged. Applying the same reflection twice returns the
    original vector.
    """

    result = list(_checked_vector(vector))
    index = _checked_coordinate(coordinate, len(result), "coordinate")
    result[index] = -result[index]
    return tuple(result)


def rotate_coordinate_plane(
    vector: Sequence[float],
    first_coordinate: int,
    second_coordinate: int,
    quarter_turns: int = 1,
) -> tuple[float, ...]:
    """Rotate a vector by exact 90-degree turns in one coordinate plane.

    Positive turns are counterclockwise in the ordered
    (first_coordinate, second_coordinate) plane: (x, y) -> (-y, x).
    Negative turns rotate clockwise. Coordinates outside that plane are
    unchanged.
    """

    result = list(_checked_vector(vector))
    first = _checked_coordinate(first_coordinate, len(result), "first_coordinate")
    second = _checked_coordinate(second_coordinate, len(result), "second_coordinate")
    if first == second:
        raise ValueError("rotation plane requires two distinct coordinates")
    if isinstance(quarter_turns, bool) or not isinstance(quarter_turns, int):
        raise TypeError("quarter_turns must be an integer")

    turns = quarter_turns % 4
    x = result[first]
    y = result[second]

    if turns == 1:
        result[first], result[second] = -y, x
    elif turns == 2:
        result[first], result[second] = -x, -y
    elif turns == 3:
        result[first], result[second] = y, -x

    return tuple(result)
