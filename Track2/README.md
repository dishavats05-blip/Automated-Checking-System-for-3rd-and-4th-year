# Track 2: The Core Stream Masters

Objective: translate raw pixel crop matrices (from Track 1's layout
segmentation) into rigid structural data - trees, graphs, and identities.

| Intern | Stream | Task | Status |
|--------|--------|------|--------|
| C | Stream A - Code Specialist | TrOCR transcription -> regex self-healing -> Tree-sitter AST | not in this drop |
| **D** | **Stream B - Diagram Nodes** | YOLOv8-obb icon detection/classification | **implemented** (`intern_d_diagram_nodes/`) |
| **E** | **Stream B - Diagram Edges** | U-Net++ line segmentation -> skeletonize -> Hough line parsing | **implemented** (`intern_e_diagram_edges/`) |
| F | Stream C - Math & Logic | Donut LaTeX transcription -> SymPy delta validation | not in this drop |

This drop covers **Intern D and Intern E only** (Stream B - Diagram
parsing). See each folder's own README for setup/usage details.

## How D and E fit together
Both consume the same `DIAGRAM_REGION` crops that Intern B's layout
segmentation step produces (`Track1/intern_a_document_vision/local_storage/extracted_crops/`),
and their outputs are meant to be merged downstream into a single diagram
graph:

```
DIAGRAM_REGION crop
        │
        ├── Intern D: YOLOv8-obb ──> nodes:  [{"id": "v0", "type": "Router", "bbox": [...]}]
        │
        └── Intern E: U-Net++ + skeleton + Hough ──> edges: [((x0,y0),(x1,y1)), ...]
                            │
                            ▼
              (next step, not in this drop: snap each edge
               endpoint to its nearest node bbox to build a
               proper graph: nodes + edges -> adjacency list)
```

## Shared output location
Both interns' inference scripts write into a shared
`Track2/local_storage/` folder (mirroring the `local_storage` convention
Intern B set up in Track 1):

```
Track2/local_storage/
├── diagram_nodes/
│   ├── <crop_name>_nodes.json
│   └── diagram_nodes_results.json     (all crops combined)
└── diagram_edges/
    ├── <crop_name>_edges.json
    └── diagram_edges_results.json     (all crops combined)
```

## Quickstart (both streams)
```bash
# Intern D
cd intern_d_diagram_nodes
pip install -r requirements.txt
python generate_dummy_diagram_data.py
python train_yolov8_diagram.py --epochs 60
python infer_diagram_nodes.py --weights model/diagram_nodes/weights/best.pt

# Intern E
cd ../intern_e_diagram_edges
pip install -r requirements.txt
python generate_dummy_edge_data.py
python train_unet_edges.py --epochs 25
python infer_diagram_edges.py --weights model/unet_edges_best.pt
```

Neither script requires the other to run first - they operate
independently on the same crop, and only need to be merged once both have
produced results for a given image.
