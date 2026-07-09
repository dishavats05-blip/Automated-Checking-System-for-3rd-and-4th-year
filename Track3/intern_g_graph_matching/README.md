# Intern G - Track 3 (Graph Theory & Programmatic Matching)

## Overview

Builds a graph representation from detected networking nodes and
connector links, then compares the student's network topology with
the reference topology using the VF2 Graph Isomorphism algorithm.

This module forms the graph evaluation stage of the automated
answer-sheet checking pipeline.

---

## Pipeline

### 1. Link Nodes and Edges

Run:

```bash
python link_nodes_edges.py
```

This module:

1. Reads detected node locations.
2. Reads connector endpoints.
3. Uses a spatial proximity algorithm to associate every edge
   endpoint with its nearest node.
4. Produces logical graph connections.

---

### 2. Build Graph

```bash
python build_graph.py
```

Creates a NetworkX graph from the linked node-edge relationships.

Each networking component becomes a graph node while every connector
becomes an edge between two nodes.

---

### 3. Graph Matching

```bash
python graph_match.py
```

Uses the VF2 Graph Isomorphism algorithm provided by NetworkX to compare

- Student topology
- Reference topology

Returns whether both graphs are structurally equivalent together with
a similarity score.

---

### 4. Graph Scoring

```bash
python score_graph.py
```

Generates the final evaluation report based on

- Graph similarity
- Node count
- Edge count
- Topology match

---

### 5. Complete Pipeline

```bash
python infer_graph.py
```

Runs the complete graph evaluation pipeline:

1. Link nodes and edges
2. Build graph
3. Compare graphs using VF2
4. Generate evaluation report

---

## Output

Produces a graph evaluation report containing

- Marks
- Grade
- Topology Match
- Student Node Count
- Reference Node Count
- Student Edge Count
- Reference Edge Count

---

## Dependencies

```bash
pip install -r requirements.txt
```

Current dependency:

```
networkx>=3.0
```

