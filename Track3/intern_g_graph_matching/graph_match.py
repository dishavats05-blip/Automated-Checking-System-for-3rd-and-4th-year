"""
Track 3 - Intern G

Graph Matching using VF2 Isomorphism Algorithm.

Compares a student's graph against the reference graph.
"""

import networkx as nx
from networkx.algorithms import isomorphism


def graphs_are_isomorphic(student_graph, reference_graph):
    """
    Returns True if both graphs are structurally identical.
    """

    matcher = isomorphism.GraphMatcher(
        student_graph,
        reference_graph
    )

    return matcher.is_isomorphic()


def matching_score(student_graph, reference_graph):
    """
    Calculate graph similarity score.

    Returns:
        {
            "isomorphic": bool,
            "student_nodes": int,
            "reference_nodes": int,
            "student_edges": int,
            "reference_edges": int,
            "score": float
        }
    """

    isomorphic = graphs_are_isomorphic(
        student_graph,
        reference_graph
    )

    student_nodes = student_graph.number_of_nodes()
    reference_nodes = reference_graph.number_of_nodes()

    student_edges = student_graph.number_of_edges()
    reference_edges = reference_graph.number_of_edges()

    score = 0.0

    if reference_nodes > 0:
        score += min(student_nodes, reference_nodes) / reference_nodes

    if reference_edges > 0:
        score += min(student_edges, reference_edges) / reference_edges

    score = (score / 2) * 100

    if isomorphic:
        score = 100.0

    return {
        "isomorphic": isomorphic,
        "student_nodes": student_nodes,
        "reference_nodes": reference_nodes,
        "student_edges": student_edges,
        "reference_edges": reference_edges,
        "score": round(score, 2)
    }


if __name__ == "__main__":

    student = nx.Graph()
    student.add_edge("N1", "N2")
    student.add_edge("N2", "N3")

    reference = nx.Graph()
    reference.add_edge("A", "B")
    reference.add_edge("B", "C")

    result = matching_score(
        student,
        reference
    )

    print("\nGraph Matching Result\n")

    for key, value in result.items():
        print(f"{key}: {value}")