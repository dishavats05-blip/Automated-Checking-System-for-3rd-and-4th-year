from celery import Celery

from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

celery_app = Celery(
    "intern_i_backend_engine",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    # Multi-track ML work (OCR, YOLO, LayoutLMv3, LLM calls) is slow and
    # heterogeneous in duration -> acknowledge late and use a modest
    # per-worker prefetch so one long diagram job doesn't starve a queue
    # of quick code-answer jobs.
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "tasks.process_script": {"queue": "pipeline"},
        "tasks.run_vision_stage": {"queue": "vision"},
        "tasks.run_extraction_stage": {"queue": "extraction"},
        "tasks.run_graph_stage": {"queue": "graph"},
        "tasks.run_llm_stage": {"queue": "llm"},
    },
)
