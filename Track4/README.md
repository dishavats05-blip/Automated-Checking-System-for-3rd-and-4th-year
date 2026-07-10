# Track 4 - Full-Stack Portal & Safeguards

Two interns close the loop between "the pipeline produced a score" and "a
professor can trust, inspect, and override that score."

- **`intern_i_backend_engine/`** — FastAPI + Celery/Redis orchestration
  layer. Accepts uploads, runs Tracks 1-3 as background jobs, computes the
  global confidence score `C_global`, and routes anything below the
  threshold (default 0.85) to a manual validation queue.
- **`intern_j_frontend_dashboard/`** — React split-screen dashboard.
  Scanned script + color-coded bounding boxes on the left, AI-extracted
  structure / marks / LLM justification on the right, with an editable
  mark field that PATCHes the backend the moment a professor overrides a
  score.

## Running both together

```bash
# Terminal 1 - Track 3 LLM/DB orchestrator (Intern H)
cd Track3/intern_h_llm_database_orchestrator && uvicorn main:app --reload --port 8000

# Terminal 2 - Redis
redis-server

# Terminal 3 - Celery worker
cd Track4/intern_i_backend_engine && celery -A celery_app worker --loglevel=info -Q pipeline,vision,extraction,graph,llm

# Terminal 4 - Track 4 backend engine (Intern I)
cd Track4/intern_i_backend_engine && uvicorn main:app --reload --port 8001

# Terminal 5 - Dashboard (Intern J)
cd Track4/intern_j_frontend_dashboard && npm install && npm run dev
```

Dashboard: `http://localhost:5173` (currently shows mock data — see that
folder's README for wiring in the live upload → poll → results flow).

## Status

- Confidence formula, Celery task graph, review queue, and override
  endpoint are implemented against the same JSON contracts Track 1-3
  already use.
- Each pipeline stage (`run_vision_stage`, `run_extraction_stage`,
  `run_graph_stage`) has its real integration point commented in-line in
  `tasks.py` — swap the placeholder body for the actual import once
  you're ready to connect a given track.
- Dashboard renders real component structure and styling against mock
  data; swapping to live data is a ~10-line change in `App.jsx`.
