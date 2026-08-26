#!/usr/bin/env python3

import unittest

from tests.hungarian_notation.fixtures import (
    STANDARD_PRIMITIVES,
    all_edges,
    case_control_edges,
    concatenate,
    standard_hungarian_edges,
)
from tests.hungarian_notation.probe import (
    case_d_minus_d_alignment,
    score_model,
    subtract,
)


class HungarianNotationFixtureTests(unittest.TestCase):
    def test_concatenation_is_literal(self) -> None:
        self.assertEqual(concatenate("c", "b", "Table"), "cbTable")
        self.assertEqual(concatenate("d", "w", "Flags"), "dwFlags")

    def test_standard_prefixes_have_declared_meanings(self) -> None:
        observed = {item.spelling: item.meaning for item in STANDARD_PRIMITIVES}
        self.assertEqual(observed["i"], "index")
        self.assertEqual(observed["cb"], "count or size in bytes")
        self.assertEqual(observed["rw"], "row number")
        self.assertEqual(observed["col"], "column number")
        self.assertEqual(observed["dw"], "DWORD-valued quantity")
        self.assertEqual(observed["w"], "WORD-valued quantity")

    def test_case_control_contains_the_exact_four_names(self) -> None:
        names = {
            name
            for edge in case_control_edges()
            for name in (edge.off_name, edge.on_name)
        }
        self.assertEqual(names, {"aBcd", "aBcD", "ABcd", "ABcD"})

    def test_standard_edges_change_exactly_one_declared_prefix(self) -> None:
        prefixes = {item.facet: item.spelling for item in STANDARD_PRIMITIVES}
        for edge in standard_hungarian_edges():
            self.assertEqual(edge.on_name, prefixes[edge.facet] + edge.off_name)


class HungarianNotationProbeTests(unittest.TestCase):
    def test_oracle_embedding_recovers_every_declared_facet(self) -> None:
        edges = all_edges()
        standard = {item.facet: item.spelling for item in STANDARD_PRIMITIVES}
        facets = sorted({edge.facet for edge in edges})

        def oracle(name: str) -> list[float]:
            values = []
            for facet in facets:
                if facet == "leading-component-uppercase":
                    values.append(float(name[0].isupper()))
                elif facet == "final-component-uppercase":
                    values.append(float(name[-1].isupper()))
                else:
                    values.append(float(name.startswith(standard[facet])))
            return values

        evidence = score_model("fixture-oracle", oracle, edges)

        self.assertEqual(evidence.facet_accuracy, 1.0)
        self.assertEqual(case_d_minus_d_alignment(evidence), 1.0)
        for facet in evidence.facets:
            self.assertEqual(facet.zero_edges, 0)
            self.assertAlmostEqual(facet.mean_leave_one_out_alignment, 1.0)

    def test_case_insensitive_model_fails_the_case_direction_explicitly(self) -> None:
        def case_insensitive(name: str) -> list[float]:
            lowered = name.lower()
            return [float(len(lowered)), float(sum(map(ord, lowered)))]

        evidence = score_model(
            "case-insensitive",
            case_insensitive,
            case_control_edges(),
        )

        self.assertIsNone(case_d_minus_d_alignment(evidence))
        final = next(
            facet
            for facet in evidence.facets
            if facet.facet == "final-component-uppercase"
        )
        self.assertEqual(final.zero_edges, 2)

    def test_model_is_called_once_per_unique_fixture_name(self) -> None:
        seen: list[str] = []

        def model(name: str) -> list[float]:
            seen.append(name)
            return [float(len(name)), float(name[0].isupper())]

        edges = case_control_edges()
        score_model("counting", model, edges)

        expected = {
            name
            for edge in edges
            for name in (edge.off_name, edge.on_name)
        }
        self.assertEqual(len(seen), len(expected))
        self.assertEqual(set(seen), expected)

    def test_subtraction_rejects_dimension_changes(self) -> None:
        with self.assertRaises(ValueError):
            subtract((1.0, 2.0), (1.0,))


if __name__ == "__main__":
    unittest.main()
