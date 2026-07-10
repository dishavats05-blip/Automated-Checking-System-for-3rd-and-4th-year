"""
Global confidence scoring.

Every question evaluation collects a confidence signal from each stage of
the pipeline. This module combines them into a single number, C_global,
which decides whether the result can go straight to the professor's
"auto-graded" view or must be routed to the manual validation queue.

    C_global = w_v * C_vision + w_e * C_extraction + w_g * C_graph + w_l * C_llm

Where each term is normalized to [0, 1]:

    C_vision      - Intern A/B: mean LayoutLMv3 region-classification
                    confidence over the regions detected for this question.
    C_extraction  - Intern C/D/E/F: OCR / AST-parse / transcription
                    confidence for the answer type actually present
                    (code -> TrOCR + parse-success, math -> LaTeX
                    transcription confidence, diagram -> node/edge
                    detection confidence).
    C_graph       - Intern G: 1.0 if the VF2 isomorphism check reports an
                    exact topology match, otherwise the reported
                    similarity score in [0, 1]. For non-diagram answers
                    this term is skipped and its weight is redistributed
                    (see `_renormalize`).
    C_llm         - Intern H: the LLM's own reported confidence label
                    (high/medium/low) mapped to a numeric value.

Any stage whose signal is missing is dropped from the weighted average and
the remaining weights are renormalized, rather than silently defaulting
that stage to 0 (which would over-penalize answer types that legitimately
skip a stage, e.g. code answers have no graph score).

If C_global falls below `CONFIDENCE_THRESHOLD`, the task is routed to the
manual validation queue instead of being marked final.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from config import CONFIDENCE_THRESHOLD, CONFIDENCE_WEIGHTS

LLM_CONFIDENCE_MAP = {"high": 1.0, "medium": 0.6, "low": 0.3}


@dataclass
class StageConfidence:
    vision: float | None = None
    extraction: float | None = None
    graph: float | None = None
    llm: float | None = None
    notes: list[str] = field(default_factory=list)


@dataclass
class GlobalConfidenceResult:
    c_global: float
    components: dict[str, float]
    weights_used: dict[str, float]
    requires_manual_review: bool
    threshold: float = CONFIDENCE_THRESHOLD


def llm_confidence_to_score(label: str) -> float:
    return LLM_CONFIDENCE_MAP.get(label.lower(), 0.5)


def _renormalize(present: dict[str, float]) -> dict[str, float]:
    total_weight = sum(CONFIDENCE_WEIGHTS[k] for k in present)
    if total_weight == 0:
        return {k: 0.0 for k in present}
    return {k: CONFIDENCE_WEIGHTS[k] / total_weight for k in present}


def compute_global_confidence(stage: StageConfidence) -> GlobalConfidenceResult:
    present = {
        name: value
        for name, value in (
            ("vision", stage.vision),
            ("extraction", stage.extraction),
            ("graph", stage.graph),
            ("llm", stage.llm),
        )
        if value is not None
    }

    if not present:
        # No signal at all from any stage -> force manual review.
        return GlobalConfidenceResult(
            c_global=0.0,
            components={},
            weights_used={},
            requires_manual_review=True,
        )

    weights = _renormalize(present)
    c_global = sum(present[name] * weights[name] for name in present)
    c_global = round(min(max(c_global, 0.0), 1.0), 4)

    return GlobalConfidenceResult(
        c_global=c_global,
        components=present,
        weights_used=weights,
        requires_manual_review=c_global < CONFIDENCE_THRESHOLD,
    )
