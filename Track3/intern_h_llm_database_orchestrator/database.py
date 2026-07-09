import os

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


DATABASE_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS course_outcomes (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS llm_evaluations (
    id SERIAL PRIMARY KEY,
    script_id VARCHAR(100) NOT NULL,
    question_id VARCHAR(50) NOT NULL,
    course_outcome VARCHAR(20) NOT NULL,
    answer_type VARCHAR(20) NOT NULL,
    programmatic_score NUMERIC NOT NULL,
    max_score NUMERIC NOT NULL,
    final_score NUMERIC NOT NULL,
    confidence VARCHAR(20) NOT NULL,
    feedback TEXT NOT NULL,
    human_review_required BOOLEAN NOT NULL DEFAULT FALSE,
    review_reason TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS human_review_overrides (
    id SERIAL PRIMARY KEY,
    script_id VARCHAR(100) NOT NULL,
    question_id VARCHAR(50) NOT NULL,
    reviewer_id VARCHAR(100) NOT NULL,
    original_score NUMERIC NOT NULL,
    corrected_score NUMERIC NOT NULL,
    max_score NUMERIC NOT NULL,
    reason TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def get_engine() -> Engine | None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return None
    return create_engine(database_url)


def initialize_database() -> bool:
    engine = get_engine()
    if engine is None:
        return False

    with engine.begin() as connection:
        for statement in DATABASE_SCHEMA_SQL.strip().split(";"):
            if statement.strip():
                connection.execute(text(statement))
    return True
