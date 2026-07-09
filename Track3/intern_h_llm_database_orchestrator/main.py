from intern_g_adapter import convert_intern_g_report
from fastapi import FastAPI

from database import DATABASE_SCHEMA_SQL, initialize_database
from llm_client import LLMClient
from schemas import (
    EvaluationRequest,
    EvaluationResponse,
    HumanOverrideRequest,
    HumanOverrideResponse,
    InternGReportRequest,
)

app = FastAPI(
    title="Track 3 Intern H - LLM and Database Orchestrator",
    description="Receives structured answer evidence, asks the LLM for final grading, and prepares data for dashboard/database use.",
    version="0.1.0",
)

llm_client = LLMClient()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "intern_h_llm_database_orchestrator"}


@app.post("/evaluate/question", response_model=EvaluationResponse)
def evaluate_question(request: EvaluationRequest) -> EvaluationResponse:
    llm_result = llm_client.grade(request)

    return EvaluationResponse(
        script_id=request.script_id,
        question_id=request.question_id,
        course_outcome=request.course_outcome,
        answer_type=request.answer_type,
        programmatic_score=request.programmatic_score.score,
        max_score=request.programmatic_score.max_score,
        final_score=llm_result["final_score"],
        confidence=llm_result["confidence"],
        feedback=llm_result["feedback"],
        detected_errors=llm_result.get("detected_errors", []),
        human_review_required=llm_result["human_review_required"],
        review_reason=llm_result.get("review_reason"),
    )

@app.post("/evaluate/intern-g-report", response_model=EvaluationResponse)
def evaluate_intern_g_report(request: InternGReportRequest) -> EvaluationResponse:
    evaluation_request = convert_intern_g_report(request)
    return evaluate_question(evaluation_request)


@app.post("/human-override", response_model=HumanOverrideResponse)
def record_human_override(request: HumanOverrideRequest) -> HumanOverrideResponse:
    return HumanOverrideResponse(
        status="recorded",
        script_id=request.script_id,
        question_id=request.question_id,
        reviewer_id=request.reviewer_id,
        corrected_score=request.corrected_score,
    )


@app.post("/database/init")
def init_database() -> dict[str, str]:
    initialized = initialize_database()
    if initialized:
        return {"status": "initialized"}
    return {"status": "skipped", "reason": "DATABASE_URL is not configured"}


@app.get("/database/schema")
def database_schema() -> dict[str, str]:
    return {"sql": DATABASE_SCHEMA_SQL}
