# Intern E - Stream B (Diagram Edges)

## Overview
Isolates connector lines out of `DIAGRAM_REGION` crops and reduces them to
per-edge terminal coordinates, using a thin U-Net++ segmentation model
followed by classical skeletonization + Hough line parsing.

## Pipeline

### 1. Generate a synthetic training set
No real annotated line-mask data exists yet, so start from synthetic
diagrams (icon blobs connected by straight/elbow lines) with matching
binary masks:

```bash
pip install -r requirements.txt
python generate_dummy_edge_data.py
```

Produces `dataset/images/{train,val}/*.png` (RGB diagrams) and
`dataset/masks/{train,val}/*.png` (binary masks, 255 = line pixel).

### 2. Train the thin U-Net++
```bash
python train_unet_edges.py --epochs 25
```
Uses `segmentation_models_pytorch.UnetPlusPlus` with a lightweight
`mobilenet_v2` encoder (kept "thin" per the spec) and a combined
BCE + Dice loss. Best weights saved to `model/unet_edges_best.pt`.

### 3. Run inference: mask -> skeleton -> Hough lines
```bash
python infer_diagram_edges.py --weights model/unet_edges_best.pt
```
For each `DIAGRAM_REGION` crop this:
1. Predicts a line-probability mask with the U-Net++, thresholds it.
2. Skeletonizes it with `skimage.morphology.skeletonize` to condense
   thick/noisy strokes to single-pixel-wide tracks.
3. Runs `cv2.HoughLinesP` over the skeleton to recover each segment's
   start/end coordinates.

By default reads crops from Intern A/B's
`local_storage/extracted_crops/` and writes results to
`../local_storage/diagram_edges/`.

## Output format
Per image, matches the spec:

```
[((x0, y0), (x1, y1)), ...]
```

Since JSON has no tuple type, this is serialized as a list of two-point
lists:

```json
[[[105, 456], [105, 206]], [[174, 415], [632, 128]]]
```

Reconstruct real tuples after loading, if needed:
```python
edges = [tuple(map(tuple, e)) for e in json.load(open(path))]
```

## Tuning notes
- `mask_to_edges()` in `infer_diagram_edges.py` exposes
  `hough_threshold`, `min_line_length`, `max_line_gap` - loosen
  `max_line_gap` if hand-drawn lines come out fragmented, raise
  `min_line_length` to drop short spurious segments near icon outlines.
- Combine with Intern D's node `bbox`/`obb` output to snap each edge
  endpoint to its nearest node for a clean graph structure.
