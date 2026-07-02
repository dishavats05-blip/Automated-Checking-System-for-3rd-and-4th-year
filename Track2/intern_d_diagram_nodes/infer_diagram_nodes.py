"""
Intern D - Stream B (Diagram Nodes)
Runs the fine-tuned YOLOv8-obb model over DIAGRAM_REGION crops (produced by
Intern B's layout segmentation step) and emits, per image, an array of node
identifiers in the exact format the rest of Track 2 expects:

    [{"id": "v0", "type": "Router", "bbox": [x0, y0, x1, y1]}, ...]

`bbox` is the axis-aligned box (min/max of the rotated OBB corners) so it
composes cleanly with downstream, non-rotation-aware consumers. The full
4-corner oriented box is kept alongside as "obb" for anything that does
care about orientation (e.g. matching Intern E's edge endpoints to the
correct side of a node).

Requires: pip install ultralytics
Usage:
    python infer_diagram_nodes.py --weights model/diagram_nodes/weights/best.pt
    python infer_diagram_nodes.py --weights best.pt --input_dir ../../Track1/intern_a_document_vision/local_storage/extracted_crops
"""

import argparse
import json
import os

from ultralytics import YOLO

DEFAULT_INPUT_DIR = os.path.join(
    "..", "..", "Track1", "intern_a_document_vision", "local_storage", "extracted_crops"
)
DEFAULT_OUTPUT_DIR = os.path.join("..", "local_storage", "diagram_nodes")


def is_diagram_crop(filename):
    return "DIAGRAM_REGION" in filename.upper() and filename.lower().endswith(
        (".png", ".jpg", ".jpeg")
    )


def obb_to_axis_aligned(corners):
    xs = [p[0] for p in corners]
    ys = [p[1] for p in corners]
    return [min(xs), min(ys), max(xs), max(ys)]


def process_image(model, image_path, conf=0.35):
    results = model.predict(source=image_path, conf=conf, verbose=False)
    nodes = []
    if not results:
        return nodes

    r = results[0]
    obb = getattr(r, "obb", None)
    if obb is None or len(obb) == 0:
        return nodes

    names = r.names
    corners_all = obb.xyxyxyxy.tolist()   # (N, 4, 2)
    cls_all = obb.cls.tolist()

    for i, (corners, cls_id) in enumerate(zip(corners_all, cls_all)):
        bbox = obb_to_axis_aligned(corners)
        nodes.append({
            "id": f"v{i}",
            "type": names[int(cls_id)],
            "bbox": [round(v, 1) for v in bbox],
            "obb": [[round(x, 1), round(y, 1)] for x, y in corners],
        })
    return nodes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights", required=True, help="Path to trained best.pt")
    parser.add_argument("--input_dir", default=DEFAULT_INPUT_DIR,
                         help="Directory of DIAGRAM_REGION crops")
    parser.add_argument("--output_dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--conf", type=float, default=0.35)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    print(f"Loading model from {args.weights}...")
    model = YOLO(args.weights)

    if not os.path.exists(args.input_dir):
        print(f"ERROR: input dir not found: {args.input_dir}")
        return

    all_results = {}
    for filename in sorted(os.listdir(args.input_dir)):
        if not is_diagram_crop(filename):
            continue
        image_path = os.path.join(args.input_dir, filename)
        print(f"Processing {filename}...")
        nodes = process_image(model, image_path, conf=args.conf)
        all_results[filename] = nodes

        per_image_path = os.path.join(
            args.output_dir, os.path.splitext(filename)[0] + "_nodes.json"
        )
        with open(per_image_path, "w") as f:
            json.dump(nodes, f, indent=2)
        print(f"  -> {len(nodes)} node(s) found, saved to {per_image_path}")

    combined_path = os.path.join(args.output_dir, "diagram_nodes_results.json")
    with open(combined_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nDone! Combined results saved to {combined_path}")


if __name__ == "__main__":
    main()
