#!/usr/bin/env python3

import unittest

from vector_transforms import reflect_coordinate, rotate_coordinate_plane


class VectorTransformTests(unittest.TestCase):
    def test_reflection_negates_only_the_selected_coordinate(self) -> None:
        vector = (1.0, -2.0, 3.0, 4.0)

        reflected = reflect_coordinate(vector, 1)

        self.assertEqual(reflected, (1.0, 2.0, 3.0, 4.0))
        self.assertEqual(reflect_coordinate(reflected, 1), vector)

    def test_positive_quarter_turn_is_counterclockwise_in_selected_plane(self) -> None:
        vector = (10.0, 2.0, 30.0, 4.0)

        rotated = rotate_coordinate_plane(vector, 1, 3)

        self.assertEqual(rotated, (10.0, -4.0, 30.0, 2.0))

    def test_negative_quarter_turn_is_clockwise(self) -> None:
        vector = (10.0, 2.0, 30.0, 4.0)

        rotated = rotate_coordinate_plane(vector, 1, 3, -1)

        self.assertEqual(rotated, (10.0, 4.0, 30.0, -2.0))

    def test_four_quarter_turns_are_exact_identity(self) -> None:
        vector = (1.25, -2.5, 3.75)

        self.assertEqual(rotate_coordinate_plane(vector, 0, 2, 4), vector)
        rotated = vector
        for _ in range(4):
            rotated = rotate_coordinate_plane(rotated, 0, 2)
        self.assertEqual(rotated, vector)

    def test_reflection_and_rotation_preserve_squared_length(self) -> None:
        vector = (1.0, 2.0, 3.0, 4.0)
        squared_length = sum(value * value for value in vector)

        reflected = reflect_coordinate(vector, 2)
        rotated = rotate_coordinate_plane(vector, 0, 3, 3)

        self.assertEqual(sum(value * value for value in reflected), squared_length)
        self.assertEqual(sum(value * value for value in rotated), squared_length)

    def test_rotation_requires_two_distinct_valid_coordinates(self) -> None:
        with self.assertRaises(ValueError):
            rotate_coordinate_plane((1.0, 2.0), 0, 0)
        with self.assertRaises(IndexError):
            rotate_coordinate_plane((1.0, 2.0), 0, 2)

    def test_coordinate_indices_and_turns_must_be_integers(self) -> None:
        with self.assertRaises(TypeError):
            reflect_coordinate((1.0, 2.0), True)
        with self.assertRaises(TypeError):
            rotate_coordinate_plane((1.0, 2.0), 0, 1, 0.5)


if __name__ == "__main__":
    unittest.main()
