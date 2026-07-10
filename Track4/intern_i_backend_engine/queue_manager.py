"""
Manual validation queue.

When `C_global < CONFIDENCE_THRESHOLD` (see confidence.py), a question is
written here instead of (or in addition to) being marked final. The
professor dashboard (Intern J) polls `GET /review-queue` to build its
work list.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

MANUAL_QUEUE_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS manual_validation_queue (
    id SERIAL PRIMARY KEY,
    script_id VARCHAR(100) NOT NULL,
    question_id VARCHAR(50) NOT NULL,
    c_global NUMERIC NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    UNIQUE (script_id, question_id)
);
"""

# In-memory fallback so the API is testable/demoable without a live
# Postgres instance. Swap for the SQL table above in production - the
# function signatures below don't change either way.
_IN_MEMORY_QUEUE: list[dict[str, Any]] = []


def _get_engine() -> Engine | None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return None
    return create_engine(database_url)


def initialize_queue_table() -> bool:
    engine = _get_engine()
    if engine is None:
        return False
    with engine.begin() as connection:
        connection.execute(text(MANUAL_QUEUE_SCHEMA_SQL))
    return True


def enqueue_for_manual_review(script_id: str, question_id: str, c_global: float, reason: str) -> None:
    engine = _get_engine()
    if engine is None:
        _IN_MEMORY_QUEUE.append(
            {
                "script_id": script_id,
                "question_id": question_id,
                "c_global": c_global,
                "reason": reason,
                "status": "pending",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        return

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO manual_validation_queue (script_id, question_id, c_global, reason)
                VALUES (:script_id, :question_id, :c_global, :reason)
                ON CONFLICT (script_id, question_id)
                DO UPDATE SET c_global = EXCLUDED.c_global, reason = EXCLUDED.reason, status = 'pending'
                """
            ),
            {"script_id": script_id, "question_id": question_id, "c_global": c_global, "reason": reason},
        )


def list_pending_reviews() -> list[dict[str, Any]]:
    engine = _get_engine()
    if engine is None:
        return [item for item in _IN_MEMORY_QUEUE if item["status"] == "pending"]

    with engine.begin() as connection:
        rows = connection.execute(
            text("SELECT * FROM manual_validation_queue WHERE status = 'pending' ORDER BY c_global ASC")
        )
        return [dict(row._mapping) for row in rows]


def resolve_review(script_id: str, question_id: str) -> None:
    engine = _get_engine()
    if engine is None:
        for item in _IN_MEMORY_QUEUE:
            if item["script_id"] == script_id and item["question_id"] == question_id:
                item["status"] = "resolved"
        return

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                UPDATE manual_validation_queue
                SET status = 'resolved', resolved_at = CURRENT_TIMESTAMP
                WHERE script_id = :script_id AND question_id = :question_id
                """
            ),
            {"script_id": script_id, "question_id": question_id},
        )
