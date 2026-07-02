# Intern D - Stream B (Diagram Nodes)

## Overview
Detects and classifies hand-drawn networking icons (Router / Switch /
Firewall / Server) inside the `DIAGRAM_REGION` crops produced by Intern B's
layout segmentation step, using a fine-tuned **YOLOv8-obb** model.

Icon vocabulary:

| Shape      | Type       |
|------------|------------|
| circle     | `Router`   |
| rectangle  | `Switch`   |
| wall (hatched block) | `Firewall` |
| cube       | `Server`   |

## Pipeline

### 1. Generate a synthetic training set
No real annotated networking-diagram data exists yet, so start from a
synthetic dataset (same approach Intern B used for layout segmentation):

```bash
pip install -r requirements.txt
python generate_dummy_diagram_data.py
```

Produces `dataset/images/{train,val}` and `dataset/labels/{train,val}` in
YOLOv8-obb label format (`class x1 y1 x2 y2 x3 y3 x4 y4`, normalized), plus
`dataset.yaml`.

### 2. Annotate real data (once available)
Use `labelstudio_config.xml` in LabelStudio to draw + rotate boxes around
icons in real `DIAGRAM_REGION` crops. Export as JSON, then convert to the
same label format:

```bash
python convert_labelstudio_to_obb.py \
    --export labelstudio_export.json \
    --images dataset/images/train \
    --labels dataset/labels/train
```

### 3. Fine-tune YOLOv8-obb
```bash
python train_yolov8_diagram.py --epochs 60
```
Best weights are saved to `model/diagram_nodes/weights/best.pt`.

### 4. Run inference & extract node list
```bash
python infer_diagram_nodes.py --weights model/diagram_nodes/weights/best.pt
```
By default reads crops from Intern A/B's
`local_storage/extracted_crops/` (any file with `DIAGRAM_REGION` in the
name) and writes results to `../local_storage/diagram_nodes/`.

## Output format
Per image, matches the spec exactly:

```json
[
  {"id": "v0", "type": "Router",   "bbox": [120.0, 40.0, 210.0, 130.0]},
  {"id": "v1", "type": "Firewall", "bbox": [300.0, 55.0, 360.0, 190.0]}
]
```

`bbox` is the axis-aligned `[x0, y0, x1, y1]` box (pixel coords in the
crop). Each node also carries an `obb` field with the full 4-corner
oriented box, for consumers (like Intern E's edge-matching step) that
care about orientation.
