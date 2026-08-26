#!/usr/bin/env python3
"""Deliberately dishonest equality oracles for integration testing only.

These are not equality implementations.  They exist so consumers can force
both ends of an equality-checking integration while also proving that emitted
warnings survive the trip.

The UTF-8 markers are intentionally provisional:

    𝕋 discrepancy
    <floating-point value>
    𝕎 warning
    <warning text>

Consumers should tolerate unrelated lines before, between, and after these
records.  The markers are handles, not a final wire-format specification.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import sys
from typing import Sequence


@dataclass(frozen=True)
class MockEqualityResult:
    discrepancy: float
    warning: str


RUBBER_STAMP_WARNING = (
    "THIS INFORMATION IS NOT TRUE: this function has not yet been implemented; "
    "rubber_stamp is a mock that reports everything as fine so integrations can "
    "force a zero-discrepancy result. Do not rely on this result."
)

CRY_WOLF_WARNING = (
    "THIS INFORMATION IS NOT TRUE: this is purely made up simply for purposes "
    "of testing other integrations. cry_wolf reports that something is wrong "
    "whether something is wrong or not. Do not rely on this result."
)


def rubber_stamp(*_ignored: object, **_ignored_named: object) -> MockEqualityResult:
    """Always approve without checking anything."""
    return MockEqualityResult(discrepancy=0.0, warning=RUBBER_STAMP_WARNING)


def cry_wolf(*_ignored: object, **_ignored_named: object) -> MockEqualityResult:
    """Always shout that the discrepancy is unbounded."""
    return MockEqualityResult(discrepancy=math.inf, warning=CRY_WOLF_WARNING)


def emit(result: MockEqualityResult) -> None:
    """Emit a small ragged-text-friendly UTF-8 record."""
    print("𝕋 discrepancy")
    print(result.discrepancy)
    print("𝕎 warning")
    print(result.warning)


def main(argv: Sequence[str]) -> int:
    if len(argv) != 2 or argv[1] not in {"rubber-stamp", "cry-wolf"}:
        print(f"usage: {argv[0]} rubber-stamp|cry-wolf", file=sys.stderr)
        return 2

    result = rubber_stamp() if argv[1] == "rubber-stamp" else cry_wolf()
    emit(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
