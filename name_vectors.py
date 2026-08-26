#!/usr/bin/env python3
"""Small vector probes for LHS/RHS name verification experiments.

This deliberately keeps the observation boundary simple.  One probe feeds the
literal LHS variable names to one or more supplied vector models and preserves
each model's coordinates by concatenation.  The other probe is a local lexical
stub for function names, so integrations can exist before a semantic name model
is chosen.

The ragged text convention used here is intentionally shallow: result first,
then optional type and warning records.  A deeper wrapper is intentionally not
chosen yet because prefix/postfix surface syntax is still under design.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence


VectorModel = Callable[[str], Sequence[float]]


@dataclass(frozen=True)
class VectorEvidence:
    vector: tuple[float, ...]
    type_info: str
    warning: str


LHS_WARNING = (
    "Prototype boundary: the supplied models see the literal LHS names and their "
    "outputs are concatenated without normalization. Coordinates from different "
    "models are not claimed to share a semantic basis."
)

FUNCTION_NAME_WARNING = (
    "Prototype boundary: this vector only proves that function names were "
    "observed. It is lexical, not semantic. Coordinate 0 is reserved as a "
    "semantic don't-care marker; its numeric 0.0 must not be interpreted as "
    "semantic zero or as evidence of equality."
)


def _checked_names(names: Sequence[str], label: str) -> tuple[str, ...]:
    checked = tuple(names)
    if not checked:
        raise ValueError(f"{label} must contain at least one name")
    if any(not isinstance(name, str) or not name for name in checked):
        raise ValueError(f"{label} must contain only non-empty strings")
    return checked


def lhs_vector(lhs_variables: Sequence[str], models: Sequence[VectorModel]) -> VectorEvidence:
    """Vectorize literal LHS variable names with one or more supplied models.

    Every model receives exactly the same newline-delimited UTF-8 Python string.
    Model outputs are concatenated rather than averaged, because unrelated
    embedding models need not use the same coordinate system.
    """

    names = _checked_names(lhs_variables, "lhs_variables")
    checked_models = tuple(models)
    if not checked_models:
        raise ValueError("models must contain at least one vector model")

    observed = "\n".join(names)
    pieces: list[tuple[float, ...]] = []
    for model in checked_models:
        piece = tuple(float(value) for value in model(observed))
        if not piece:
            raise ValueError("a vector model returned an empty vector")
        pieces.append(piece)

    vector = tuple(value for piece in pieces for value in piece)
    dimensions = "+".join(str(len(piece)) for piece in pieces)
    return VectorEvidence(
        vector=vector,
        type_info=(
            f"vector/python-float[{len(vector)}]; lhs-name-model-concat="
            f"{dimensions}; models={len(pieces)}"
        ),
        warning=LHS_WARNING,
    )


def function_name_vector(function_names: Sequence[str]) -> VectorEvidence:
    """Emit a deterministic lexical stub vector for one or more function names.

    Coordinate 0 is intentionally reserved for later semantic information and
    is currently a don't-care.  The remaining coordinates are plain counts, so
    a human can inspect exactly what this stub measured.
    """

    names = _checked_names(function_names, "function_names")
    joined = "\n".join(names)

    vector = (
        0.0,  # reserved semantic coordinate: unknown/don't-care, not semantic zero
        float(len(names)),
        float(sum(len(name) for name in names)),
        float(len(joined.encode("utf-8"))),
        float(sum(name.count("_") for name in names)),
        float(sum(character.isdigit() for name in names for character in name)),
        float(sum(character.isupper() for name in names for character in name)),
        float(sum(character.islower() for name in names for character in name)),
        float(sum(1 for name in names for character in name if not character.isalnum())),
    )

    return VectorEvidence(
        vector=vector,
        type_info=(
            "vector/python-float[9]; dim0=semantic-dont-care; "
            "dims1..8=lexical-counts"
        ),
        warning=FUNCTION_NAME_WARNING,
    )


def emit(evidence: VectorEvidence) -> None:
    """Emit ragged result/type/warning evidence without defining a wrapper ABI."""

    print("[" + ", ".join(repr(value) for value in evidence.vector) + "]")
    print()
    print("𝕋 " + evidence.type_info)
    print()
    print("𝕎 " + evidence.warning)


# TODO: consider a tiny wrapper for ragged result/𝕋/𝕎 emission after the
# language's prefix/postfix surface form is clearer.  Do not make that wrapper
# a semantic requirement of these probes yet.
