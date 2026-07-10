from __future__ import annotations

import os
import uuid
from pathlib import Path

import httpx
from celery.result import AsyncResult
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from celery_app import celery_app
from config import INTERN_H_BASE_URL, UPLOAD_DIR
from queue_manager import initialize_queue_table, list_pending_reviews
from schemas import (
    ScoreOverridePatch,
    ScoreOverrideResponse,
    TaskState,
    TaskStatusResponse,
    UploadResponse,
)
from tasks import process_script

app = FastAPI(
    title="Track 4 Intern I - Backend Orchestration Engine",
    description=(
        "Accepts scanned-script uploads, fans the multi-track ML pipeline "
        "out to Celery/Redis workers, tracks task state, and exposes "
        "results + the manual-review queue to the professor dashboard."
    ),
    version="0.1.0",
)

# The React dashboard (Intern J) runs on a different origin during dev.
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

# task_id -> script_id, so the dashboard can poll by either.
_TASK_INDEX: dict[str, str] = {}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "intern_i_backend_engine"}


@app.post("/upload", response_model=UploadResponse)
async def upload_script(file: UploadFile) -> UploadResponse:
    """Accepts a scanned answer script (PDF or image) and queues it for
    background processing. Returns immediately with a task_id to poll."""
    script_id = str(uuid.uuid4())
    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    destination = Path(UPLOAD_DIR) / f"{script_id}_{file.filename}"

    contents = await file.read()
    destination.write_bytes(contents)

    async_result = process_script.delay(script_id, str(destination))
    _TASK_INDEX[async_result.id] = script_id

    return UploadResponse(script_id=script_id, task_id=async_result.id, filename=file.filename)


@app.get("/tasks/{task_id}", response_model=TaskStatusResponse)
def get_task_status(task_id: str) -> TaskStatusResponse:
    """Poll for pipeline progress. Maps Celery's native states onto the
    dashboard's simplified state machine."""
    result = AsyncResult(task_id, app=celery_app)
    script_id = _TASK_INDEX.get(task_id, "unknown")

    state_map: dict[str, TaskState] = {
        "PENDING": "QUEUED",
        "STARTED": "PROCESSING",
        "RETRY": "PROCESSING",
        "SUCCESS": "DONE",
        "FAILURE": "FAILED",
    }
    state: TaskState = state_map.get(result.state, "PROCESSING")

    error = str(result.result) if result.failed() else None

    if state == "DONE" and isinstance(result.result, dict):
        questions = result.result.get("questions", [])
        if any(q.get("human_review_required") for q in questions):
            state = "NEEDS_REVIEW"

    return TaskStatusResponse(task_id=task_id, script_id=script_id, state=state, error=error)


@app.get("/results/{task_id}")
def get_results(task_id: str) -> dict:
    """Returns the completed pipeline output for a task, shaped for the
    dashboard (see schemas.ScriptResultResponse). Used once GET
    /tasks/{task_id} reports state=DONE or NEEDS_REVIEW."""
    result = AsyncResult(task_id, app=celery_app)
    if not result.ready():
        raise HTTPException(status_code=409, detail="Task is not finished yet")
    if result.failed():
        raise HTTPException(status_code=500, detail=str(result.result))
    return result.result


@app.get("/review-queue")

def get_review_queue() -> list[dict]:
    """Everything currently below the C_global threshold, sorted lowest
    confidence first - this is the professor's work queue."""
    return list_pending_reviews()


@app.patch("/scripts/{script_id}/questions/{question_id}/score", response_model=ScoreOverrideResponse)
def override_score(script_id: str, question_id: str, patch: ScoreOverridePatch) -> ScoreOverrideResponse:
    """Bound to the dashboard's editable mark field (Intern J). Forwards
    the correction to Intern H's /human-override endpoint so it lands in
    the same `human_review_overrides` table used for audit/analytics,
    then confirms back to the frontend so the UI can update instantly."""
    with httpx.Client(base_url=INTERN_H_BASE_URL, timeout=30) as client:
        response = client.post(
            "/human-override",
            json={
                "script_id": script_id,
                "question_id": question_id,
                "reviewer_id": patch.reviewer_id,
                "original_score": 0,  # dashboard should pass the pre-edit score in a real call
                "corrected_score": patch.corrected_score,
                "max_score": 10,
                "reason": patch.reason,
            },
        )
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        upstream = response.json()

    return ScoreOverrideResponse(
        status="recorded",
        script_id=script_id,
        question_id=question_id,
        reviewer_id=patch.reviewer_id,
        corrected_score=upstream["corrected_score"],
    )


@app.post("/database/init")
def init_database() -> dict[str, str]:
    initialized = initialize_queue_table()
    return {"status": "initialized" if initialized else "skipped (DATABASE_URL not set)"}
