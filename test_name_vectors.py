#!/usr/bin/env python3

import io
import unittest
from contextlib import redirect_stdout

from name_vectors import emit, function_name_vector, lhs_vector


class NameVectorTests(unittest.TestCase):
    def test_lhs_vector_shows_models_the_literal_same_names(self) -> None:
        seen: list[str] = []

        def model_a(text: str) -> list[float]:
            seen.append(text)
            return [len(text), text.count("\n")]

        def model_b(text: str) -> list[float]:
            seen.append(text)
            return [text.count("x")]

        result = lhs_vector(["x", "velocity"], [model_a, model_b])

        self.assertEqual(seen, ["x\nvelocity", "x\nvelocity"])
        self.assertEqual(result.vector, (10.0, 1.0, 1.0))
        self.assertIn("models=2", result.type_info)
        self.assertIn("not claimed to share a semantic basis", result.warning)

    def test_function_name_vector_is_deterministic_and_observes_names(self) -> None:
        first = function_name_vector(["read_file", "HTTP2"])
        second = function_name_vector(["read_file", "HTTP2"])
        different = function_name_vector(["write_file", "HTTP2"])

        self.assertEqual(first, second)
        self.assertNotEqual(first.vector, different.vector)
        self.assertEqual(first.vector[0], 0.0)
        self.assertIn("dim0=semantic-dont-care", first.type_info)
        self.assertIn("must not be interpreted as semantic zero", first.warning)

    def test_x_does_not_claim_semantic_zero(self) -> None:
        result = function_name_vector(["x"])

        self.assertEqual(result.vector[0], 0.0)
        self.assertEqual(result.vector[1], 1.0)
        self.assertEqual(result.vector[2], 1.0)
        self.assertIn("don't-care", result.warning)

    def test_emit_keeps_result_before_type_and_warning(self) -> None:
        result = function_name_vector(["x"])
        output = io.StringIO()

        with redirect_stdout(output):
            emit(result)

        rendered = output.getvalue()
        self.assertLess(rendered.index("["), rendered.index("𝕋 "))
        self.assertLess(rendered.index("𝕋 "), rendered.index("𝕎 "))


if __name__ == "__main__":
    unittest.main()
