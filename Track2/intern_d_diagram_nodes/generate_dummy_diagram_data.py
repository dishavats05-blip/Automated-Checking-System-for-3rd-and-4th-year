"""
Intern D - Stream B (Diagram Nodes)
Generates a synthetic dataset of hand-drawn-style networking icons so the
YOLOv8-obb model has something to train on before real annotated
DIAGRAM_REGION crops are available (mirrors Intern B's
generate_dummy_data.py approach for LayoutLMv3).

Icon vocabulary (matches the spec):
    circle    -> Router
    rectangle -> Switch
    wall      -> Firewall   (hatched vertical block)
    cube      -> Server     (pseudo-3D box)

Labels are written in YOLOv8-OBB format:
    class_id x1 y1 x2 y2 x3 y3 x4 y4      (all coords normalized 0-1)

Output layout (matches what train_yolov8_diagram.py / dataset.yaml expect):
    dataset/images/train/*.png
    dataset/images/val/*.png
    dataset/labels/train/*.txt
    dataset/labels/val/*.txt
"""

import os
import json
import math
import random

import cv2
import numpy as np

CLASSES = ["Router", "Switch", "Firewall", "Server"]
CLASS_ID = {name: i for i, name in enumerate(CLASSES)}

IMG_W, IMG_H = 800, 600
N_TRAIN = 150
N_VAL = 30
MAX_ROT_DEG = 12          # small skew to mimic hand-drawn imprecision
MIN_ICONS, MAX_ICONS = 3, 6

DATA_DIR = os.path.join("dataset")


def rotated_corners(cx, cy, w, h, theta_deg):
    """Return the 4 corners of a (w x h) box centered at (cx, cy),
    rotated by theta_deg, as a (4, 2) array of (x, y)."""
    theta = math.radians(theta_deg)
    local = np.array([
        [-w / 2, -h / 2],
        [w / 2, -h / 2],
        [w / 2, h / 2],
        [-w / 2, h / 2],
    ])
    rot = np.array([
        [math.cos(theta), -math.sin(theta)],
        [math.sin(theta), math.cos(theta)],
    ])
    world = local @ rot.T + np.array([cx, cy])
    return world


def draw_router(canvas, corners):
    cx, cy = corners.mean(axis=0)
    r = int(min(np.linalg.norm(corners[0] - corners[1]),
                np.linalg.norm(corners[1] - corners[2])) / 2)
    cv2.circle(canvas, (int(cx), int(cy)), r, (40, 40, 40), 2)
    # inner "signal" arcs to look router-ish
    cv2.circle(canvas, (int(cx), int(cy)), max(2, r // 3), (40, 40, 40), 2)


def draw_switch(canvas, corners):
    pts = corners.astype(np.int32).reshape(-1, 1, 2)
    cv2.polylines(canvas, [pts], True, (40, 40, 40), 2)
    # port ticks along the bottom edge
    p0, p1 = corners[3], corners[2]
    for t in np.linspace(0.15, 0.85, 5):
        x, y = p0 + t * (p1 - p0)
        cv2.line(canvas, (int(x), int(y) - 4), (int(x), int(y) + 4), (40, 40, 40), 1)


def draw_firewall(canvas, corners):
    pts = corners.astype(np.int32).reshape(-1, 1, 2)
    cv2.polylines(canvas, [pts], True, (40, 40, 40), 2)
    # brick / hatch pattern = "wall"
    top, bottom = corners[0], corners[3]
    n_lines = 5
    for i in range(1, n_lines):
        t = i / n_lines
        a = corners[0] + t * (corners[3] - corners[0])
        b = corners[1] + t * (corners[2] - corners[1])
        cv2.line(canvas, tuple(a.astype(int)), tuple(b.astype(int)), (40, 40, 40), 1)


def draw_server(canvas, corners):
    # pseudo-3D cube: front face = corners, plus offset top/side face
    pts = corners.astype(np.int32).reshape(-1, 1, 2)
    cv2.polylines(canvas, [pts], True, (40, 40, 40), 2)
    offset = (corners[1] - corners[0]) * 0.25
    normal = np.array([-offset[1], offset[0]]) * 0.4
    back = corners + normal
    for i in range(4):
        cv2.line(canvas, tuple(corners[i].astype(int)), tuple(back[i].astype(int)), (40, 40, 40), 1)
    top_pts = np.array([corners[0], corners[1], back[1], back[0]]).astype(np.int32).reshape(-1, 1, 2)
    cv2.polylines(canvas, [top_pts], True, (40, 40, 40), 1)


DRAW_FN = {
    "Router": draw_router,
    "Switch": draw_switch,
    "Firewall": draw_firewall,
    "Server": draw_server,
}

# rough (w, h) footprint per icon type
SIZE_RANGE = {
    "Router": (70, 70, 100, 100),
    "Switch": (90, 50, 140, 80),
    "Firewall": (50, 90, 70, 140),
    "Server": (70, 90, 100, 130),
}


def place_icons(canvas):
    labels = []
    n_icons = random.randint(MIN_ICONS, MAX_ICONS)
    placed_boxes = []

    attempts = 0
    while len(labels) < n_icons and attempts < n_icons * 20:
        attempts += 1
        cls = random.choice(CLASSES)
        w_lo, h_lo, w_hi, h_hi = SIZE_RANGE[cls]
        w = random.randint(w_lo, w_hi)
        h = random.randint(h_lo, h_hi)
        cx = random.randint(w, IMG_W - w)
        cy = random.randint(h, IMG_H - h)

        # avoid heavy overlap with already-placed icons
        overlap = False
        for (bx, by, bw, bh) in placed_boxes:
            if abs(cx - bx) < (w + bw) * 0.55 and abs(cy - by) < (h + bh) * 0.55:
                overlap = True
                break
        if overlap:
            continue

        theta = random.uniform(-MAX_ROT_DEG, MAX_ROT_DEG)
        corners = rotated_corners(cx, cy, w, h, theta)
        DRAW_FN[cls](canvas, corners)
        placed_boxes.append((cx, cy, w, h))
        labels.append((cls, corners))

    return labels


def to_yolo_obb_line(cls_name, corners):
    norm = corners.copy().astype(np.float64)
    norm[:, 0] /= IMG_W
    norm[:, 1] /= IMG_H
    norm = np.clip(norm, 0.0, 1.0)
    coords = " ".join(f"{v:.6f}" for v in norm.flatten())
    return f"{CLASS_ID[cls_name]} {coords}"


def generate_split(split_name, n_images, start_id=0):
    img_dir = os.path.join(DATA_DIR, "images", split_name)
    lbl_dir = os.path.join(DATA_DIR, "labels", split_name)
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(lbl_dir, exist_ok=True)

    for i in range(n_images):
        img_id = start_id + i
        canvas = np.full((IMG_H, IMG_W, 3), 255, dtype=np.uint8)
        labels = place_icons(canvas)

        img_name = f"diagram_{img_id:04d}.png"
        cv2.imwrite(os.path.join(img_dir, img_name), canvas)

        lbl_name = f"diagram_{img_id:04d}.txt"
        with open(os.path.join(lbl_dir, lbl_name), "w") as f:
            for cls_name, corners in labels:
                f.write(to_yolo_obb_line(cls_name, corners) + "\n")

        print(f"[{split_name}] generated {img_name} ({len(labels)} icons)")


def write_dataset_yaml():
    yaml_path = "dataset.yaml"
    lines = [
        f"path: ./{DATA_DIR}",
        "train: images/train",
        "val: images/val",
        "names:",
    ]
    for idx, name in enumerate(CLASSES):
        lines.append(f"  {idx}: {name}")
    with open(yaml_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Wrote {yaml_path}")


if __name__ == "__main__":
    random.seed(42)
    generate_split("train", N_TRAIN, start_id=0)
    generate_split("val", N_VAL, start_id=N_TRAIN)
    write_dataset_yaml()
    print(f"\nDone! {N_TRAIN} train / {N_VAL} val images generated in {DATA_DIR}/")
