from schemas import EvaluationRequest, InternGReportRequest, ProgrammaticScore


def convert_intern_g_report(report: InternGReportRequest) -> EvaluationRequest:
    normalized_score = round((report.marks / 100) * 10, 2)
    intern_g_report = report.model_dump(by_alias=True)

    return EvaluationRequest(
        student_id=report.student_id,
        script_id=report.script_id,
        question_id=report.question_id,
        course_outcome=report.course_outcome,
        answer_type="diagram",
        programmatic_score=ProgrammaticScore(
            score=normalized_score,
            max_score=10,
            method="vf2_graph_isomorphism",
            details={
                "grade": report.grade,
                "topology_match": report.topology_match,
                "student_nodes": report.student_nodes,
                "reference_nodes": report.reference_nodes,
                "student_edges": report.student_edges,
                "reference_edges": report.reference_edges,
                "raw_marks_percent": report.marks,
            },
        ),
        structural_payload={"intern_g_report": intern_g_report},
        master_answer={},
    )