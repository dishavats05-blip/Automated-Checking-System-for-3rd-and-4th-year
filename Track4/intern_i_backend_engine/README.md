# Intern I - Backend Orchestration Engine

Async FastAPI layer that sits in front of the whole pipeline (Tracks 1-3).
It accepts an upload, hands the heavy ML work to Celery workers backed by
Redis, tracks task state, computes the global confidence score, and routes
low-confidence results to a manual validation queue for the professor
dashboard (Intern J).

## Architecture

```
Upload (PDF/image)
   │
   ▼
POST /upload  ──────────────►  Celery task: tasks.process_script
   │  returns task_id                │
   │                                 ▼
   │                        run_vision_stage      (queue: vision)     Track 1
   │                                 │
   │                                 ▼
   │                        run_extraction_stage   (queue: extraction) Track 2
   │                                 │
   │                                 ▼
   │                        run_graph_stage         (queue: graph)     Track 3 (Intern G)
   │                                 │
   │                                 ▼
   │                        run_llm_stage            (queue: llm)      Track 3 (Intern H, via HTTP)
   │                                 │
   │                                 ▼
   │                     compute C_global per question (confidence.py)
   │                                 │
   │                     C_global < 0.85 ──► manual_validation_queue
   │
   ▼
GET /tasks/{task_id}   -> poll status
GET /review-queue      -> professor's manual work list
PATCH /scripts/{id}/questions/{qid}/score -> professor override
```

Each stage is its own Celery task on its own queue (`vision`, `extraction`,
`graph`, `llm`) so a slow diagram job never blocks a fast code-answer job
sitting behind it. `tasks.py` currently has each stage's real integration
point commented in-line (import + call), ready to be uncommented once each
track's module is imported.

## Global confidence formula

```
C_global = w_v * C_vision + w_e * C_extraction + w_g * C_graph + w_l * C_llm
```

Default weights: vision 0.15, extraction 0.30, graph 0.25, llm 0.30 (sum
1.0, tunable via env vars). Any stage that doesn't apply to a given answer
type (e.g. no graph score for a code answer) is dropped and the remaining
weights are renormalized rather than treated as a zero. See
`confidence.py` for the full derivation and `CONFIDENCE_THRESHOLD` (default
`0.85`) for the manual-review cutoff.

## Setup

```bash
pip install -r requirements.txt

# 1. Start Redis (broker + result backend)
redis-server

# 2. Start a Celery worker (separate terminal)
celery -A celery_app worker --loglevel=info -Q pipeline,vision,extraction,graph,llm

# 3. Start the API (separate terminal) - use a different port than
#    Intern H's orchestrator, which defaults to 8000
uvicorn main:app --reload --port 8001
```

Open `http://127.0.0.1:8001/docs` for the interactive API. Make sure Intern
H's service (`Track3/intern_h_llm_database_orchestrator`) is running on
`:8000` first, since `run_llm_stage` calls it over HTTP.

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `REDIS_URL` | `redis://localhost:6379/0` | Celery broker + result backend |
| `INTERN_H_BASE_URL` | `http://localhost:8000` | Track 3 LLM/DB orchestrator (Intern H) — run it on a different port locally |
| `DATABASE_URL` | unset | Postgres URL for the manual validation queue table; falls back to an in-memory queue if unset |
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed origins for the React dashboard |
| `C_WEIGHT_VISION` / `_EXTRACTION` / `_GRAPH` / `_LLM` | `0.15` / `0.30` / `0.25` / `0.30` | Confidence formula weights |
| `CONFIDENCE_THRESHOLD` | `0.85` | Below this, route to manual review |

## Endpoints

- `POST /upload` — multipart file upload, returns `{script_id, task_id}`
- `GET /tasks/{task_id}` — poll status: `QUEUED / PROCESSING / DONE / NEEDS_REVIEW / FAILED`
- `GET /review-queue` — pending manual-review items, lowest confidence first
- `PATCH /scripts/{script_id}/questions/{question_id}/score` — professor override, forwarded to Intern H's `/human-override` and persisted to the audit table
- `GET /results/{task_id}` — full pipeline output once a task is finished
- `POST /database/init` — creates the `manual_validation_queue` table
