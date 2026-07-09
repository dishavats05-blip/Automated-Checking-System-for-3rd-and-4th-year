import json

from schemas import EvaluationRequest


SYSTEM_PROMPTS = {
    "code": """You are an exam-grading assistant for handwritten CSE code answers.
Use the AST, transcription, syntax checks, and programmatic score as evidence.
Reward correct algorithmic logic and partial correctness. Penalize missing cases,
wrong control flow, and syntax that changes meaning.""",
    "diagram": """You are an exam-grading assistant for CSE diagram answers.
Use graph nodes, graph edges, topology matching, and VF2/isomorphism score as
evidence. Reward equivalent topology even if drawing layout differs.""",
    "math": """You are an exam-grading assistant for handwritten math derivations.
Use LaTeX, SymPy validation, step deltas, and final-answer equivalence as evidence.
Reward valid intermediate reasoning and identify the first incorrect step.""",
    "mixed": """You are an exam-grading assistant for mixed CSE answers.
Combine code, diagram, math, and prose evidence. Do not invent evidence missing
from the structured payload.""",
}


REQUIRED_JSON_FORMAT = {
    "final_score": "number",
    "confidence": "high | medium | low",
    "feedback": "short student-facing feedback",
    "detected_errors": ["error 1", "error 2"],
    "human_review_required": "boolean",
    "review_reason": "string or null",
}


def build_grading_prompt(request: EvaluationRequest) -> str:
    system_prompt = SYSTEM_PROMPTS[request.answer_type]
    evidence = request.model_dump()

    return f"""{system_prompt}

Return only valid JSON in this exact shape:
{json.dumps(REQUIRED_JSON_FORMAT, indent=2)}

Evidence:
{json.dumps(evidence, indent=2)}
"""
