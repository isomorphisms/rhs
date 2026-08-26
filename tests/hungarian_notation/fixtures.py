"""Controlled Hungarian-notation name fixtures.

Historical prefixes are kept separate from the synthetic capitalization cube.
The historical fixture records the intended meaning of each prefix. The case
cube exists because its transformation is mechanically unambiguous, not
because aBcd is claimed to be a historical Hungarian identifier.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HungarianPrimitive:
    spelling: str
    facet: str
    meaning: str
    family: str


@dataclass(frozen=True)
class FacetEdge:
    facet: str
    meaning: str
    off_name: str
    on_name: str
    context: str


STANDARD_PRIMITIVES: tuple[HungarianPrimitive, ...] = (
    HungarianPrimitive("i", "index", "index", "semantic"),
    HungarianPrimitive("cb", "byte-count", "count or size in bytes", "semantic"),
    HungarianPrimitive("rw", "row", "row number", "semantic"),
    HungarianPrimitive("col", "column", "column number", "semantic"),
    HungarianPrimitive("dw", "DWORD", "DWORD-valued quantity", "type"),
    HungarianPrimitive("w", "WORD", "WORD-valued quantity", "type"),
)


_CONTEXTS: dict[str, tuple[str, ...]] = {
    "index": ("Item", "Position", "Entry", "Cursor"),
    "byte-count": ("Buffer", "Packet", "Table", "Message"),
    "row": ("Position", "Start", "End", "Cursor"),
    "column": ("Position", "Start", "End", "Cursor"),
    "DWORD": ("Flags", "Mask", "Style", "Value"),
    "WORD": ("Flags", "Mask", "Style", "Value"),
}


def concatenate(*parts: str) -> str:
    """Concatenate name primitives without silently coercing non-strings."""

    if not parts:
        raise ValueError("at least one name primitive is required")
    if any(not isinstance(part, str) for part in parts):
        raise TypeError("name primitives must be strings")
    return "".join(parts)


def standard_hungarian_edges() -> tuple[FacetEdge, ...]:
    """Generate controlled prefix-on versus prefix-off edges."""

    edges: list[FacetEdge] = []
    for primitive in STANDARD_PRIMITIVES:
        for stem in _CONTEXTS[primitive.facet]:
            edges.append(
                FacetEdge(
                    facet=primitive.facet,
                    meaning=primitive.meaning,
                    off_name=stem,
                    on_name=concatenate(primitive.spelling, stem),
                    context=stem,
                )
            )
    return tuple(edges)


def case_control_edges() -> tuple[FacetEdge, ...]:
    """Return the exact 2x2 capitalization control discussed for D-d."""

    return (
        FacetEdge(
            facet="leading-component-uppercase",
            meaning="capitalize the leading A/a component",
            off_name="aBcd",
            on_name="ABcd",
            context="final component d",
        ),
        FacetEdge(
            facet="leading-component-uppercase",
            meaning="capitalize the leading A/a component",
            off_name="aBcD",
            on_name="ABcD",
            context="final component D",
        ),
        FacetEdge(
            facet="final-component-uppercase",
            meaning="capitalize the final D/d component",
            off_name="aBcd",
            on_name="aBcD",
            context="leading component a",
        ),
        FacetEdge(
            facet="final-component-uppercase",
            meaning="capitalize the final D/d component",
            off_name="ABcd",
            on_name="ABcD",
            context="leading component A",
        ),
    )


def all_edges() -> tuple[FacetEdge, ...]:
    return standard_hungarian_edges() + case_control_edges()
