"""
Background pipeline tasks.

`process_script` is the entry point queued by the FastAPI upload endpoint.
It chains the four track stages together. Each stage is its own Celery
task (and its own queue, see celery_app.py) so that, e.g., a slow diagram
job in the "graph" queue doesn't block code-answer jobs still waiting on
"extraction".

Each *_stage task is a thin adapter around the real Track 1/2/3 modules.
They are written against the JSON contracts already defined by Interns
A-H (crop paths, node/edge lists, EvaluationRequest/-Response) so wiring
in the real implementations is a matter of importing them, not
redesigning the interface.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from celery_app import celery_app
from confidence import StageConfidence, compute_global_confidence, llm_confidence_to_score
from config import INTERN_H_BASE_URL
from queue_manager import enqueue_for_manual_review

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.run_vision_stage", bind=True, max_retries=2)
def run_vision_stage(self, script_id: str, file_path: str) -> dict[str, Any]:
    """Track 1 (Intern A/B): PDF/image -> clean -> deskew -> anonymize ->
    layout segmentation. Returns per-region crops + a mean detection
    confidence used as C_vision."""
    try:
        # from Track1.intern_a_document_vision.src.main import run_intake_pipeline
        # from Track1.intern_a_document_vision.intern_b.infer_layoutlmv3 import segment_layout
        # cleaned = run_intake_pipeline(file_path)
        # regions = segment_layout(cleaned)
        regions: list[dict[str, Any]] = []  # placeholder until wired to real modules
        mean_confidence = (
            sum(r.get("confidence", 0.0) for r in regions) / len(regions) if regions else None
        )
        return {"script_id": script_id, "regions": regions, "c_vision": mean_confidence}
    except Exception as exc:  # noqa: BLE001
        logger.exception("Vision stage failed for %s", script_id)
        raise self.retry(exc=exc, countdown=10)


@celery_app.task(name="tasks.run_extraction_stage", bind=True, max_retries=2)
def run_extraction_stage(self, vision_result: dict[str, Any]) -> dict[str, Any]:
    """Track 2 (Intern C/D/E/F): per-region OCR/AST/diagram-node/edge/math
    extraction, routed by region_type. Returns structural payloads keyed
    by question_id plus a mean extraction confidence (C_extraction)."""
    try:
        extracted: dict[str, Any] = {}
        confidences: list[float] = []
        for region in vision_result.get("regions", []):
            region_type = region.get("region_type")
            # if region_type == "CODE_CANVAS": from Track2.Intern_c.main import run as extract_code
            # if region_type == "DIAGRAM_REGION": from Track2.intern_d_diagram_nodes... / intern_e_diagram_edges...
            # if region_type == "MATH_REGION": from Track2.intern_f.src.pipeline import transcribe_validate
            # result = extract_code(region) / infer_diagram_nodes(region) / transcribe_validate(region)
            # extracted[region["question_id"]] = result
            # confidences.append(result.get("confidence", 0.0))
            pass
        c_extraction = sum(confidences) / len(confidences) if confidences else None
        return {
            "script_id": vision_result["script_id"],
            "extracted": extracted,
            "c_extraction": c_extraction,
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("Extraction stage failed")
        raise self.retry(exc=exc, countdown=10)


@celery_app.task(name="tasks.run_graph_stage", bind=True, max_retries=2)
def run_graph_stage(self, extraction_result: dict[str, Any]) -> dict[str, Any]:
    """Track 3 (Intern G): for diagram questions, link nodes/edges, build
    the graph, run VF2 isomorphism against the reference topology.
    Non-diagram questions pass through untouched (no C_graph term)."""
    try:
        graph_scores: dict[str, Any] = {}
        # from Track3.intern_g_graph_matching.infer_graph import run_graph_pipeline
        # for question_id, payload in extraction_result["extracted"].items():
        #     if payload.get("answer_type") == "diagram":
        #         graph_scores[question_id] = run_graph_pipeline(payload)
        return {**extraction_result, "graph_scores": graph_scores}
    except Exception as exc:  # noqa: BLE001
        logger.exception("Graph stage failed")
        raise self.retry(exc=exc, countdown=10)


@celery_app.task(name="tasks.run_llm_stage", bind=True, max_retries=2)
def run_llm_stage(self, graph_result: dict[str, Any]) -> dict[str, Any]:
    """Track 3 (Intern H): call the LLM/database orchestrator service for
    each question, then compute C_global and route to manual review if
    needed."""
    script_id = graph_result["script_id"]
    final_questions: list[dict[str, Any]] = []

    for question_id, payload in graph_result.get("extracted", {}).items():
        evaluation_request = _build_evaluation_request(script_id, question_id, payload, graph_result)

        with httpx.Client(base_url=INTERN_H_BASE_URL, timeout=60) as client:
            response = client.post("/evaluate/question", json=evaluation_request)
            response.raise_for_status()
            llm_response = response.json()

        stage_confidence = StageConfidence(
            vision=graph_result.get("c_vision"),
            extraction=graph_result.get("c_extraction"),
            graph=graph_result.get("graph_scores", {}).get(question_id, {}).get("similarity_score"),
            llm=llm_confidence_to_score(llm_response["confidence"]),
        )
        result = compute_global_confidence(stage_confidence)

        question_record = {
            **llm_response,
            "c_global": result.c_global,
            "confidence_components": result.components,
            "human_review_required": llm_response["human_review_required"] or result.requires_manual_review,
        }
        final_questions.append(question_record)

        if result.requires_manual_review:
            enqueue_for_manual_review(
                script_id=script_id,
                question_id=question_id,
                c_global=result.c_global,
                reason=llm_response.get("review_reason") or "C_global below threshold",
            )

    return {"script_id": script_id, "questions": final_questions}


def _build_evaluation_request(
    script_id: str, question_id: str, payload: dict[str, Any], graph_result: dict[str, Any]
) -> dict[str, Any]:
    return {
        "script_id": script_id,
        "question_id": question_id,
        "course_outcome": payload.get("course_outcome", "CO1"),
        "answer_type": payload.get("answer_type", "mixed"),
        "programmatic_score": payload.get("programmatic_score", {"score": 0, "max_score": 10}),
        "structural_payload": payload.get("structural_payload", {}),
        "master_answer": payload.get("master_answer", {}),
    }


@celery_app.task(name="tasks.process_script", bind=True)
def process_script(self, script_id: str, file_path: str) -> dict[str, Any]:
    """Chains all four stages. Kept as a single task (rather than a
    Celery `chain(...)`) so the FastAPI layer has one task_id to poll,
    while each helper above still runs as its own task via `.apply()` /
    `.delay()` chaining internally in a real deployment. For clarity here
    it calls the stages directly; swap for `chain(...).apply_async()` if
    each stage should be retried/scaled independently."""
    vision_result = run_vision_stage.run(script_id, file_path)
    extraction_result = run_extraction_stage.run(vision_result)
    graph_result = run_graph_stage.run(extraction_result)
    final_result = run_llm_stage.run(graph_result)
    return final_result
