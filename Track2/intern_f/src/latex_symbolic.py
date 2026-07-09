from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sympy import Eq, simplify
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)


@dataclass
class ParsedEquation:
    expression: Any
    latex: str


def parse_latex_expression(latex_text: str) -> Any:
    try:
        from sympy.parsing.latex import parse_latex
    except Exception as exc:
        raise RuntimeError("sympy latex parser is unavailable") from exc

    try:
        return parse_latex(latex_text)
    except Exception:
        return _parse_simple_expression(latex_text)


def _parse_simple_expression(text: str) -> Any:
    transformations = standard_transformations + (
        convert_xor,
        implicit_multiplication_application,
    )

    cleaned_text = text.replace("\\left", "").replace("\\right", "")
    if "=" in cleaned_text:
        left_text, right_text = cleaned_text.split("=", 1)
        return Eq(
            parse_expr(left_text.strip(), transformations=transformations),
            parse_expr(right_text.strip(), transformations=transformations),
        )

    return parse_expr(cleaned_text.strip(), transformations=transformations)


def build_equation(latex_text: str) -> ParsedEquation:
    expression = parse_latex_expression(latex_text)
    return ParsedEquation(expression=expression, latex=latex_text)


def _to_difference(expression: Any) -> Any:
    if isinstance(expression, Eq):
        return expression.lhs - expression.rhs
    return expression


def simplify_delta(student_expression: Any, reference_expression: Any) -> Any:
    student_difference = _to_difference(student_expression)
    reference_difference = _to_difference(reference_expression)
    return simplify(student_difference - reference_difference)


def equations_are_equivalent(student_expression: Any, reference_expression: Any) -> bool:
    return simplify_delta(student_expression, reference_expression) == 0


def equation_step_is_valid(student_latex: str, reference_latex: str) -> bool:
    student = build_equation(student_latex).expression
    reference = build_equation(reference_latex).expression

    return equations_are_equivalent(student, reference)
