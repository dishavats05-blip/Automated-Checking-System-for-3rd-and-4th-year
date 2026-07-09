"""
Track 3 - Intern G

Graph Scoring Module

Generates the final marks based on the graph
matching results.
"""


def calculate_score(match_result):
    """
    Convert graph matching result into marks.
    """

    score = match_result["score"]

    if score >= 95:
        grade = "Excellent"

    elif score >= 80:
        grade = "Good"

    elif score >= 60:
        grade = "Average"

    elif score >= 40:
        grade = "Poor"

    else:
        grade = "Fail"

    return {
        "Marks": score,
        "Grade": grade,
        "Topology Match": match_result["isomorphic"],
        "Student Nodes": match_result["student_nodes"],
        "Reference Nodes": match_result["reference_nodes"],
        "Student Edges": match_result["student_edges"],
        "Reference Edges": match_result["reference_edges"]
    }


def print_report(report):

    print("\n==============================")
    print(" GRAPH EVALUATION REPORT")
    print("==============================\n")

    for key, value in report.items():
        print(f"{key:20}: {value}")

    print("\n==============================\n")


if __name__ == "__main__":

    sample_result = {
        "isomorphic": True,
        "student_nodes": 3,
        "reference_nodes": 3,
        "student_edges": 2,
        "reference_edges": 2,
        "score": 100.0
    }

    report = calculate_score(sample_result)

    print_report(report)