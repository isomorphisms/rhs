#!/usr/bin/env python3
"""Run the Hungarian-notation facet probe against Hugging Face encoders."""

from __future__ import annotations

import argparse
import json
from typing import Callable, Sequence

from tests.hungarian_notation.fixtures import all_edges
from tests.hungarian_notation.probe import (
    ModelEvidence,
    case_d_minus_d_alignment,
    score_model,
)


DEFAULT_MODELS = (
    "microsoft/codebert-base",
    "huggingface/CodeBERTa-small-v1",
    "sentence-transformers/all-MiniLM-L6-v2",
    "bert-base-cased",
    "bert-base-uncased",
)


def huggingface_encoder(
    model_id: str,
    device: str = "cpu",
) -> Callable[[str], Sequence[float]]:
    """Load one encoder and expose the RHS probe's text -> vector boundary."""

    try:
        import torch
        from transformers import AutoModel, AutoTokenizer
    except ImportError as error:
        raise SystemExit(
            "This optional experiment requires torch and transformers."
        ) from error

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    encoder = AutoModel.from_pretrained(model_id)
    encoder.to(device)
    encoder.eval()

    def embed(text: str) -> list[float]:
        encoded = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=64,
        )
        encoded = {key: value.to(device) for key, value in encoded.items()}
        with torch.no_grad():
            hidden = encoder(**encoded).last_hidden_state
        mask = encoded["attention_mask"].unsqueeze(-1).to(hidden.dtype)
        pooled = (hidden * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1)
        return pooled[0].detach().cpu().tolist()

    return embed


def _jsonable(evidence: ModelEvidence, include_vectors: bool) -> dict[str, object]:
    facets = [
        {
            "facet": item.facet,
            "meaning": item.meaning,
            "edge_count": item.edge_count,
            "zero_edges": item.zero_edges,
            "mean_leave_one_out_alignment": item.mean_leave_one_out_alignment,
            "prototype_norm": item.prototype_norm,
            **({"prototype": item.prototype} if include_vectors else {}),
        }
        for item in evidence.facets
    ]
    edges = [
        {
            "facet": item.edge.facet,
            "meaning": item.edge.meaning,
            "off": item.edge.off_name,
            "on": item.edge.on_name,
            "context": item.edge.context,
            "difference_norm": item.norm,
            "predicted_facet": item.predicted_facet,
            **({"difference_vector": item.vector} if include_vectors else {}),
        }
        for item in evidence.edges
    ]
    return {
        "model": evidence.model_name,
        "pooling": "last hidden state, attention-mask mean",
        "facet_accuracy": evidence.facet_accuracy,
        "correct_edges": evidence.correct_edges,
        "total_edges": evidence.total_edges,
        "D_minus_d_context_alignment": case_d_minus_d_alignment(evidence),
        "facets": facets,
        "edges": edges,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        action="append",
        dest="models",
        help="Hugging Face model id; repeat to compare models",
    )
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--include-vectors", action="store_true")
    arguments = parser.parse_args()

    model_ids = tuple(arguments.models or DEFAULT_MODELS)
    reports = []
    for model_id in model_ids:
        model = huggingface_encoder(model_id, arguments.device)
        evidence = score_model(model_id, model, all_edges())
        reports.append(_jsonable(evidence, arguments.include_vectors))

    print(json.dumps(reports, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
