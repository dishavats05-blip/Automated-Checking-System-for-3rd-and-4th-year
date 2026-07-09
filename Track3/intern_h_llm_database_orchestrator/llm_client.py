from __future__ import annotations

import json
import os
from typing import Any

import requests

from llm_prompts import build_grading_prompt
from schemas import EvaluationRequest


class LLMClient:
    """Uses a real LLM endpoint when configured, otherwise returns a safe mock result."""

    def __init__(self) -> None:
        self.endpoint = os.getenv("LLM_ENDPOINT")
        self.timeout_seconds = int(os.getenv("LLM_TIMEOUT_SECONDS", "60"))

    def grade(self, request: EvaluationRequest) -> dict[str, Any]:
        if not self.endpoint:
            return self._mock_grade(request)

        prompt = build_grading_prompt(request)
        response = requests.post(
            self.endpoint,
            json={"prompt": prompt, "temperature": 0.1},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        text = payload.get("response") or payload.get("text") or payload

        if isinstance(text, dict):
            return text

        return json.loads(text)

    def _mock_grade(self, request: EvaluationRequest) -> dict[str, Any]:
        score = request.programmatic_score.score
        max_score = request.programmatic_score.max_score
        ratio = score / max_score

        detected_errors: list[str] = []
        human_review_required = False
        review_reason = None

        if ratio < 0.4:
            detected_errors.append("Answer has low structural similarity with the master answer.")

        if not request.structural_payload:
            human_review_required = True
            review_reason = "No structural payload was provided for LLM verification."

        confidence = "high" if ratio >= 0.75 and not human_review_required else "medium"
        if ratio < 0.4 or human_review_required:
            confidence = "low"

        return {
            "final_score": round(score, 2),
            "confidence": confidence,
            "feedback": (
                f"Programmatic evaluation gives {score}/{max_score}. "
                "Final LLM-backed review can be enabled after configuring LLM_ENDPOINT."
            ),
            "detected_errors": detected_errors,
            "human_review_required": human_review_required,
            "review_reason": review_reason,
        }
