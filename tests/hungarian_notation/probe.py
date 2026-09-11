"""Score whether one embedding model gives repeatable directions to name facets."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable, Iterable, Sequence

from .fixtures import FacetEdge


Vector = tuple[float, ...]
VectorModel = Callable[[str], Sequence[float]]


@dataclass(frozen=True)
class EdgeEvidence:
    edge: FacetEdge
    vector: Vector
    norm: float
    predicted_facet: str | None


@dataclass(frozen=True)
class FacetEvidence:
    facet: str
    meaning: str
    edge_count: int
    zero_edges: int
    mean_leave_one_out_alignment: float | None
    prototype: Vector
    prototype_norm: float


@dataclass(frozen=True)
class ModelEvidence:
    model_name: str
    facet_accuracy: float
    correct_edges: int
    total_edges: int
    facets: tuple[FacetEvidence, ...]
    edges: tuple[EdgeEvidence, ...]


def _vector(values: Sequence[float]) -> Vector:
    result = tuple(float(value) for value in values)
    if not result:
        raise ValueError("model returned an empty vector")
    if any(not math.isfinite(value) for value in result):
        raise ValueError("model returned a non-finite coordinate")
    return result


def subtract(left: Sequence[float], right: Sequence[float]) -> Vector:
    """Return left-right in one model's coordinate system."""

    left_vector = _vector(left)
    right_vector = _vector(right)
    if len(left_vector) != len(right_vector):
        raise ValueError("vectors must have the same dimensions")
    return tuple(a - b for a, b in zip(left_vector, right_vector))


def mean_vector(vectors: Iterable[Sequence[float]]) -> Vector:
    checked = tuple(_vector(vector) for vector in vectors)
    if not checked:
        raise ValueError("at least one vector is required")
    dimensions = len(checked[0])
    if any(len(vector) != dimensions for vector in checked):
        raise ValueError("vectors must have the same dimensions")
    return tuple(
        sum(vector[index] for vector in checked) / len(checked)
        for index in range(dimensions)
    )


def norm(vector: Sequence[float]) -> float:
    checked = _vector(vector)
    return math.sqrt(sum(value * value for value in checked))


def cosine(left: Sequence[float], right: Sequence[float]) -> float | None:
    """Cosine similarity, or None when either direction is the zero vector."""

    left_vector = _vector(left)
    right_vector = _vector(right)
    if len(left_vector) != len(right_vector):
        raise ValueError("vectors must have the same dimensions")
    left_norm = norm(left_vector)
    right_norm = norm(right_vector)
    if left_norm == 0.0 or right_norm == 0.0:
        return None
    return sum(a * b for a, b in zip(left_vector, right_vector)) / (
        left_norm * right_norm
    )


def _prototype(
    indices: Sequence[int],
    vectors: Sequence[Vector],
    *,
    omit: int | None = None,
) -> Vector | None:
    chosen = [vectors[index] for index in indices if index != omit]
    return mean_vector(chosen) if chosen else None


def score_model(
    model_name: str,
    model: VectorModel,
    edges: Sequence[FacetEdge],
) -> ModelEvidence:
    """Measure direction consistency and leave-one-edge-out facet recovery.

    Each edge is always on-off. A facet therefore has a declared meaning before
    a learned model is consulted. The model is judged on whether independent
    contexts produce a repeatable direction for that declared transformation.
    """

    checked_edges = tuple(edges)
    if not checked_edges:
        raise ValueError("edges must not be empty")

    # Real Hugging Face encoders are expensive. Repeated fixture names are
    # embedded exactly once, while the subtraction experiment remains explicit.
    names = dict.fromkeys(
        name
        for edge in checked_edges
        for name in (edge.off_name, edge.on_name)
    )
    embeddings = {name: _vector(model(name)) for name in names}
    dimensions = {len(vector) for vector in embeddings.values()}
    if len(dimensions) != 1:
        raise ValueError("one model returned inconsistent vector dimensions")

    edge_vectors = tuple(
        subtract(embeddings[edge.on_name], embeddings[edge.off_name])
        for edge in checked_edges
    )

    groups: dict[str, list[int]] = {}
    meanings: dict[str, str] = {}
    for index, edge in enumerate(checked_edges):
        groups.setdefault(edge.facet, []).append(index)
        previous = meanings.setdefault(edge.facet, edge.meaning)
        if previous != edge.meaning:
            raise ValueError(f"facet {edge.facet!r} has conflicting meanings")

    facet_evidence: list[FacetEvidence] = []
    for facet in sorted(groups):
        indices = groups[facet]
        prototype = mean_vector(edge_vectors[index] for index in indices)
        alignments: list[float] = []
        zero_edges = 0
        for index in indices:
            if norm(edge_vectors[index]) == 0.0:
                zero_edges += 1
            other = _prototype(indices, edge_vectors, omit=index)
            if other is not None:
                alignment = cosine(edge_vectors[index], other)
                if alignment is not None:
                    alignments.append(alignment)

        facet_evidence.append(
            FacetEvidence(
                facet=facet,
                meaning=meanings[facet],
                edge_count=len(indices),
                zero_edges=zero_edges,
                mean_leave_one_out_alignment=(
                    sum(alignments) / len(alignments) if alignments else None
                ),
                prototype=prototype,
                prototype_norm=norm(prototype),
            )
        )

    predictions: list[str | None] = []
    correct = 0
    tie_tolerance = 1e-12

    for target_index, target_vector in enumerate(edge_vectors):
        if norm(target_vector) == 0.0:
            predictions.append(None)
            continue

        similarities: list[tuple[float, str]] = []
        for facet in sorted(groups):
            candidate = _prototype(
                groups[facet],
                edge_vectors,
                omit=target_index if target_index in groups[facet] else None,
            )
            if candidate is None:
                continue
            similarity = cosine(target_vector, candidate)
            if similarity is not None:
                similarities.append((similarity, facet))

        if not similarities:
            predictions.append(None)
            continue

        similarities.sort(reverse=True)
        best_similarity, best_facet = similarities[0]
        if (
            len(similarities) > 1
            and abs(best_similarity - similarities[1][0]) <= tie_tolerance
        ):
            predictions.append(None)
            continue

        predictions.append(best_facet)
        if best_facet == checked_edges[target_index].facet:
            correct += 1

    edge_evidence = tuple(
        EdgeEvidence(
            edge=edge,
            vector=edge_vectors[index],
            norm=norm(edge_vectors[index]),
            predicted_facet=predictions[index],
        )
        for index, edge in enumerate(checked_edges)
    )

    return ModelEvidence(
        model_name=model_name,
        facet_accuracy=correct / len(checked_edges),
        correct_edges=correct,
        total_edges=len(checked_edges),
        facets=tuple(facet_evidence),
        edges=edge_evidence,
    )


def case_d_minus_d_alignment(evidence: ModelEvidence) -> float | None:
    """Compare the two D-d edges from aBcd/aBcD and ABcd/ABcD."""

    edges = [
        item
        for item in evidence.edges
        if item.edge.facet == "final-component-uppercase"
    ]
    if len(edges) != 2:
        raise ValueError("expected exactly two final-component-uppercase controls")
    return cosine(edges[0].vector, edges[1].vector)
