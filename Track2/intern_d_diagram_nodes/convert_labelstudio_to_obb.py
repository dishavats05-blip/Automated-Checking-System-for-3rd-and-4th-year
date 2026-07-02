"""
Intern D - Stream B (Diagram Nodes)
Converts a LabelStudio JSON export (produced with labelstudio_config.xml)
into YOLOv8-obb label .txt files, so real annotated data can be dropped
straight into the same dataset/ layout that
generate_dummy_diagram_data.py produces.

Usage:
    python convert_labelstudio_to_obb.py --export path/to/export.json \
        --images dataset/images/train --labels dataset/labels/train
"""

import argparse
import json
import math
import os

import numpy as np
from PIL import Image

from generate_dummy_diagram_data import CLASS_ID  # reuse the shared label map


def rect_to_obb_corners(x_pct, y_pct, w_pct, h_pct, rotation_deg, img_w, img_h):
    """LabelStudio rectangle: (x, y) is the top-left corner in % before
    rotation, rotation is applied clockwise around that top-left corner."""
    x0 = x_pct / 100 * img_w
    y0 = y_pct / 100 * img_h
    w = w_pct / 100 * img_w
    h = h_pct / 100 * img_h

    local = np.array([
        [0, 0],
        [w, 0],
        [w, h],
        [0, h],
    ])
    theta = math.radians(rotation_deg)
    rot = np.array([
        [math.cos(theta), -math.sin(theta)],
        [math.sin(theta), math.cos(theta)],
    ])
    world = local @ rot.T + np.array([x0, y0])
    return world


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--export", required=True, help="LabelStudio JSON export path")
    parser.add_argument("--images", required=True, help="Directory containing the source images")
    parser.add_argument("--labels", required=True, help="Directory to write YOLO-obb .txt files")
    args = parser.parse_args()

    os.makedirs(args.labels, exist_ok=True)

    with open(args.export, "r", encoding="utf-8") as f:
        tasks = json.load(f)

    actual_images = {f.lower(): f for f in os.listdir(args.images)
                      if f.lower().endswith((".png", ".jpg", ".jpeg"))}

    for task in tasks:
        ls_path = task["data"]["image"]
        ls_filename = os.path.basename(ls_path).lower()

        image_name = None
        for actual_lower, actual_name in actual_images.items():
            if actual_lower in ls_filename or ls_filename.endswith(actual_lower):
                image_name = actual_name
                break
        if image_name is None:
            print(f"Warning: could not match {ls_filename} to a file in {args.images}, skipping")
            continue

        img_path = os.path.join(args.images, image_name)
        with Image.open(img_path) as im:
            img_w, img_h = im.size

        lines = []
        for ann in task.get("annotations", [{}])[0].get("result", []):
            value = ann["value"]
            label = value["rectanglelabels"][0]
            if label not in CLASS_ID:
                print(f"Warning: unknown label '{label}', skipping region")
                continue
            corners = rect_to_obb_corners(
                value["x"], value["y"], value["width"], value["height"],
                value.get("rotation", 0.0), img_w, img_h,
            )
            norm = corners.copy()
            norm[:, 0] /= img_w
            norm[:, 1] /= img_h
            norm = np.clip(norm, 0.0, 1.0)
            coords = " ".join(f"{v:.6f}" for v in norm.flatten())
            lines.append(f"{CLASS_ID[label]} {coords}")

        out_name = os.path.splitext(image_name)[0] + ".txt"
        with open(os.path.join(args.labels, out_name), "w") as f:
            f.write("\n".join(lines) + ("\n" if lines else ""))
        print(f"Wrote {out_name} ({len(lines)} icons)")


if __name__ == "__main__":
    main()
