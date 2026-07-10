from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

TaskState = Literal["QUEUED", "PROCESSING", "DONE", "FAILED", "NEEDS_REVIEW"]


class UploadResponse(BaseModel):
    script_id: str
    task_id: str
    filename: str
    status: TaskState = "QUEUED"
    submitted_at: datetime = Field(default_factory=datetime.utcnow)


class TaskStatusResponse(BaseModel):
    task_id: str
    script_id: str
    state: TaskState
    progress: dict[str, str] = Field(default_factory=dict)
    error: str | None = None


class BoundingBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float
    region_type: str  # PROSE_TEXT | CODE_CANVAS | DIAGRAM_REGION | MATH_REGION
    question_id: str | None = None


class QuestionResult(BaseModel):
    question_id: str
    course_outcome: str
    answer_type: Literal["code", "diagram", "math", "mixed"]
    programmatic_score: float
    max_score: float
    final_score: float
    llm_confidence: Literal["high", "medium", "low"]
    c_global: float
    confidence_components: dict[str, float] = Field(default_factory=dict)
    human_review_required: bool
    review_reason: str | None = None
    feedback: str
    detected_errors: list[str] = Field(default_factory=list)
    structural_payload: dict[str, Any] = Field(default_factory=dict)
    bounding_boxes: list[BoundingBox] = Field(default_factory=list)


class ScriptResultResponse(BaseModel):
    script_id: str
    student_id: str
    page_image_url: str
    total_score: float
    total_max_score: float
    questions: list[QuestionResult]


class ScoreOverridePatch(BaseModel):
    reviewer_id: str
    corrected_score: float
    reason: str


class ScoreOverrideResponse(BaseModel):
    status: str
    script_id: str
    question_id: str
    reviewer_id: str
    corrected_score: float
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
