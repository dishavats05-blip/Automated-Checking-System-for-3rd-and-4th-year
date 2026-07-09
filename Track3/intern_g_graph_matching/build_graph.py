"""
Track 3 - Intern G

Build a NetworkX graph from the linked node-edge data.

Input:
[
    {
        "edge_id": "E1",
        "source": "N1",
        "target": "N2"
    }
]

Output:
NetworkX Graph
"""

import networkx as nx


def build_graph(linked_edges):
    """
    Build and return a NetworkX graph.
    """

    graph = nx.Graph()

    for edge in linked_edges:

        source = edge["source"]
        target = edge["target"]

        # Add nodes
        graph.add_node(source)
        graph.add_node(target)

        # Add edge
        graph.add_edge(
            source,
            target,
            edge_id=edge.get("edge_id", "")
        )

    return graph


def print_graph(graph):
    """
    Print graph information.
    """

    print("\nNodes")
    print("----------------")

    for node in graph.nodes():
        print(node)

    print("\nEdges")
    print("----------------")

    for edge in graph.edges():
        print(edge)


if __name__ == "__main__":

    linked_connections = [
        {
            "edge_id": "E1",
            "source": "N1",
            "target": "N2"
        },
        {
            "edge_id": "E2",
            "source": "N2",
            "target": "N3"
        }
    ]

    graph = build_graph(linked_connections)

    print_graph(graph)