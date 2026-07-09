# Track 3: Intern H - LLM and Database Orchestrator

This module is the final evaluation layer for the automated answer checking
system. It receives structured outputs from earlier tracks, combines them with
programmatic scores, prepares an LLM grading prompt, returns final feedback, and
defines the PostgreSQL schema needed for dashboard and human-review workflows.

## Responsibilities

- Accept Track 1/2/3G structured JSON evidence.
- Use answer-type specific prompts for code, diagram, math, and mixed answers.
- Return final marks, feedback, confidence, errors, and review flags.
- Prepare PostgreSQL tables for LLM evaluations and human overrides.
- Support human-in-the-loop correction through an override endpoint.

## Setup

From the repository root:

```bash
venv\Scripts\activate
cd Track3\intern_h_llm_database_orchestrator
uvicorn main:app --reload
```

Open this in the browser:

```text
http://127.0.0.1:8000/docs
```

## Test Input

Use `POST /evaluate/question` with this sample:

```json
{
  "student_id": "masked",
  "script_id": "script_001",
  "question_id": "Q3",
  "course_outcome": "CO2",
  "answer_type": "diagram",
  "programmatic_score": {
    "score": 7,
    "max_score": 10,
    "method": "vf2_graph_isomorphism",
    "details": {
      "matched_nodes": 4,
      "missing_edges": 1
    }
  },
  "structural_payload": {
    "nodes": [
      {"id": "v0", "type": "Router"},
      {"id": "v1", "type": "Switch"}
    ],
    "edges": [["v0", "v1"]]
  },
  "master_answer": {
    "expected_nodes": ["Router", "Switch", "Server"],
    "expected_edges": [["Router", "Switch"], ["Switch", "Server"]]
  }
}
```

## Real LLM Connection

By default, this project uses a mock LLM response so the API can run immediately.
When the GPU-hosted Llama service is available, set:

```bash
set LLM_ENDPOINT=http://your-llama-server/generate
```

Then restart the FastAPI server.

## PostgreSQL

Set `DATABASE_URL` before calling `POST /database/init`:

```bash
set DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/anrf_grading
```
