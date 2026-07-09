from __future__ import annotations

from itertools import zip_longest
from dataclasses import dataclass
from typing import List

from .latex_symbolic import equation_step_is_valid, simplify_delta


@dataclass
class ValidationResult:
    student_latex: str
    reference_latex: str
    is_valid: bool
    delta: str


def validate_equation_step(student_latex: str, reference_latex: str) -> ValidationResult:
    from .latex_symbolic import build_equation

    student_expr = build_equation(student_latex).expression
    reference_expr = build_equation(reference_latex).expression
    delta = simplify_delta(student_expr, reference_expr)

    return ValidationResult(
        student_latex=student_latex,
        reference_latex=reference_latex,
        is_valid=equation_step_is_valid(student_latex, reference_latex),
        delta=str(delta),
    )


def validate_step_sequence(student_steps: List[str], reference_steps: List[str]) -> List[ValidationResult]:
    results: List[ValidationResult] = []
    for student_latex, reference_latex in zip_longest(student_steps, reference_steps, fillvalue=None):
        if student_latex is None:
            results.append(
                ValidationResult(
                    student_latex="",
                    reference_latex=reference_latex or "",
                    is_valid=False,
                    delta="missing student step",
                )
            )
            continue

        if reference_latex is None:
            results.append(
                ValidationResult(
                    student_latex=student_latex,
                    reference_latex="",
                    is_valid=False,
                    delta="unexpected extra student step",
                )
            )
            continue

        results.append(validate_equation_step(student_latex, reference_latex))
    return results
