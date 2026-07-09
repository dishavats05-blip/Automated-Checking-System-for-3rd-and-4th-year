"""
Track 3 - Intern G

Complete Graph Matching Pipeline

Pipeline:
1. Link nodes and edges
2. Build NetworkX graph
3. Compare with reference graph (VF2)
4. Generate score report
"""

import networkx as nx

from link_nodes_edges import link_nodes_and_edges
from build_graph import build_graph
from graph_match import matching_score
from score_graph import calculate_score, print_report


def create_reference_graph():
    """
    Temporary reference graph.
    Later this will come from the teacher's answer key.
    """

    reference = nx.Graph()

    reference.add_edge("N1", "N2")
    reference.add_edge("N2", "N3")

    return reference


def main():

    nodes = [
        {
            "id": "N1",
            "label": "Router",
            "bbox": [100, 100, 180, 180]
        },
        {
            "id": "N2",
            "label": "Switch",
            "bbox": [300, 100, 380, 180]
        },
        {
            "id": "N3",
            "label": "Server",
            "bbox": [200, 300, 280, 380]
        }
    ]

    edges = [
        {
            "id": "E1",
            "points": [
                [140, 140],
                [340, 140]
            ]
        },
        {
            "id": "E2",
            "points": [
                [340, 150],
                [240, 330]
            ]
        }
    ]

    print("\nStep 1 : Linking Nodes and Edges...")
    linked_edges = link_nodes_and_edges(nodes, edges)

    print("Done.")

    print("\nStep 2 : Building Student Graph...")
    student_graph = build_graph(linked_edges)

    print("Done.")

    print("\nStep 3 : Building Reference Graph...")
    reference_graph = create_reference_graph()

    print("Done.")

    print("\nStep 4 : Running VF2 Graph Matching...")
    result = matching_score(student_graph, reference_graph)

    print("Done.")

    print("\nStep 5 : Generating Report...")
    report = calculate_score(result)

    print_report(report)


if __name__ == "__main__":
    main()