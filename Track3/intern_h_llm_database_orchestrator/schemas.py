from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


AnswerType = Literal["code", "diagram", "math", "mixed"]


class ProgrammaticScore(BaseModel):
    score: float = Field(ge=0)
    max_score: float = Field(gt=0)
    method: str = "programmatic"
    details: dict[str, Any] = Field(default_factory=dict)


class EvaluationRequest(BaseModel):
    student_id: str = "masked"
    script_id: str
    question_id: str
    course_outcome: str
    answer_type: AnswerType
    programmatic_score: ProgrammaticScore
    structural_payload: dict[str, Any] = Field(default_factory=dict)
    master_answer: dict[str, Any] = Field(default_factory=dict)

class InternGReportRequest(BaseModel):
    student_id: str = "masked"
    script_id: str
    question_id: str
    course_outcome: str
    marks: float = Field(alias="Marks", ge=0)
    grade: str = Field(alias="Grade")
    topology_match: bool = Field(alias="Topology Match")
    student_nodes: int = Field(alias="Student Nodes", ge=0)
    reference_nodes: int = Field(alias="Reference Nodes", ge=0)
    student_edges: int = Field(alias="Student Edges", ge=0)
    reference_edges: int = Field(alias="Reference Edges", ge=0)


class EvaluationResponse(BaseModel):
    script_id: str
    question_id: str
    course_outcome: str
    answer_type: AnswerType
    programmatic_score: float
    max_score: float
    final_score: float
    confidence: Literal["high", "medium", "low"]
    feedback: str
    detected_errors: list[str] = Field(default_factory=list)
    human_review_required: bool
    review_reason: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class HumanOverrideRequest(BaseModel):
    script_id: str
    question_id: str
    reviewer_id: str
    original_score: float
    corrected_score: float
    max_score: float
    reason: str


class HumanOverrideResponse(BaseModel):
    status: str
    script_id: str
    question_id: str
    reviewer_id: str
    corrected_score: float
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
