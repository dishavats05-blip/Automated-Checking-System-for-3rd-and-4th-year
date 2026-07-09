"""
Intern G - Spatial Node Edge Linking

This module links detected edges with detected nodes using
spatial proximity.

Input:
nodes = [
    {
        "id": "N1",
        "label": "Router",
        "bbox": [x1, y1, x2, y2]
    }
]

edges = [
    {
        "id": "E1",
        "points": [
            [x1, y1],
            [x2, y2]
        ]
    }
]

Output:
[
    {
        "edge_id": "E1",
        "source": "N1",
        "target": "N2"
    }
]
"""

import math


def point_inside_bbox(point, bbox):
    """
    Check if point lies inside a bounding box.
    bbox = [x1,y1,x2,y2]
    """

    x, y = point
    x1, y1, x2, y2 = bbox

    return x1 <= x <= x2 and y1 <= y <= y2


def bbox_center(bbox):
    x1, y1, x2, y2 = bbox

    return (
        (x1 + x2) / 2,
        (y1 + y2) / 2
    )


def euclidean_distance(p1, p2):

    return math.sqrt(
        (p1[0] - p2[0]) ** 2 +
        (p1[1] - p2[1]) ** 2
    )


def nearest_node(point, nodes):
    """
    Return nearest node id.
    """

    best_node = None
    best_distance = float("inf")

    for node in nodes:

        centre = bbox_center(node["bbox"])

        d = euclidean_distance(point, centre)

        if d < best_distance:
            best_distance = d
            best_node = node["id"]

    return best_node


def endpoint_to_node(point, nodes):
    """
    Convert endpoint into node.
    """

    for node in nodes:

        if point_inside_bbox(point, node["bbox"]):
            return node["id"]

    return nearest_node(point, nodes)


def link_nodes_and_edges(nodes, edges):
    """
    Main linking algorithm.
    """

    connections = []

    for edge in edges:

        start = edge["points"][0]
        end = edge["points"][-1]

        source = endpoint_to_node(start, nodes)
        target = endpoint_to_node(end, nodes)

        if source == target:
            continue

        connection = {
            "edge_id": edge["id"],
            "source": source,
            "target": target
        }

        if connection not in connections:
            connections.append(connection)

    return connections


if __name__ == "__main__":

    sample_nodes = [
        {
            "id": "N1",
            "label": "Router",
            "bbox": [100,100,180,180]
        },
        {
            "id": "N2",
            "label": "Switch",
            "bbox": [300,100,380,180]
        },
        {
            "id": "N3",
            "label": "Server",
            "bbox": [200,300,280,380]
        }
    ]

    sample_edges = [
        {
            "id":"E1",
            "points":[
                [140,140],
                [340,140]
            ]
        },
        {
            "id":"E2",
            "points":[
                [340,150],
                [240,330]
            ]
        }
    ]

    result = link_nodes_and_edges(sample_nodes, sample_edges)

    print("\nLinked Connections\n")

    for r in result:
        print(r)