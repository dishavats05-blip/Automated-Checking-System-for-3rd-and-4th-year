from __future__ import annotations

import unittest

from src.equation_validator import validate_equation_step, validate_step_sequence
from src.latex_symbolic import equation_step_is_valid


class EquationValidatorTests(unittest.TestCase):
    def test_equivalent_equations_are_valid(self) -> None:
        self.assertTrue(equation_step_is_valid(r"x^2 + y^2 = z^2", r"x^2 + y^2 - z^2 = 0"))

    def test_non_equivalent_equations_are_rejected(self) -> None:
        self.assertFalse(equation_step_is_valid(r"x^2 + y^2 = z^2 + 1", r"x^2 + y^2 - z^2 = 0"))

    def test_validate_equation_step_returns_delta(self) -> None:
        result = validate_equation_step(r"x^2 + y^2 = z^2", r"x^2 + y^2 - z^2 = 0")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.delta, "0")

    def test_validate_step_sequence_processes_pairs(self) -> None:
        student_steps = [r"x^2 + y^2 = z^2", r"x^2 + y^2 - z^2 = 0"]
        reference_steps = [r"x^2 + y^2 = z^2", r"x^2 + y^2 - z^2 = 0"]

        results = validate_step_sequence(student_steps, reference_steps)

        self.assertEqual(len(results), 2)
        self.assertTrue(all(result.is_valid for result in results))

    def test_validate_step_sequence_flags_misalignment(self) -> None:
        student_steps = [r"x^2 + y^2 = z^2"]
        reference_steps = [r"x^2 + y^2 = z^2", r"x^2 + y^2 - z^2 = 0"]

        results = validate_step_sequence(student_steps, reference_steps)

        self.assertEqual(len(results), 2)
        self.assertTrue(results[0].is_valid)
        self.assertFalse(results[1].is_valid)
        self.assertEqual(results[1].delta, "missing student step")


if __name__ == "__main__":
    unittest.main()
