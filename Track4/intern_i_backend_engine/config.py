import os

# --- Message broker / result backend --------------------------------------
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

# --- Storage ----------------------------------------------------------------
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "storage/uploads")
CROPS_DIR = os.getenv("CROPS_DIR", "storage/crops")

# --- Downstream services ----------------------------------------------------
# Track 3 / Intern H orchestrator (LLM + database layer)
INTERN_H_BASE_URL = os.getenv("INTERN_H_BASE_URL", "http://localhost:8000")

# --- Global confidence formula ----------------------------------------------
# C_global = w_v*C_vision + w_e*C_extraction + w_g*C_graph + w_l*C_llm
# Weights must sum to 1.0; see confidence.py for the full derivation.
CONFIDENCE_WEIGHTS = {
    "vision": float(os.getenv("C_WEIGHT_VISION", "0.15")),
    "extraction": float(os.getenv("C_WEIGHT_EXTRACTION", "0.30")),
    "graph": float(os.getenv("C_WEIGHT_GRAPH", "0.25")),
    "llm": float(os.getenv("C_WEIGHT_LLM", "0.30")),
}

# Below this, a task is routed straight to the manual validation queue
# instead of being auto-published to the student/professor as "final".
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.85"))
