"""
Intern E - Stream B (Diagram Edges)
Generates a synthetic dataset of diagram images (icon-like blobs connected
by straight/elbow lines) paired with binary line masks, so the thin
U-Net++ segmentation model has something to train on before real
annotated DIAGRAM_REGION crops are available.

Output layout:
    dataset/images/train/*.png   (RGB diagram crop, white background)
    dataset/masks/train/*.png    (binary mask, 255 = line pixel, 0 = bg)
    dataset/images/val/*.png
    dataset/masks/val/*.png
"""

import os
import random

import cv2
import numpy as np

IMG_W, IMG_H = 800, 600
N_TRAIN = 150
N_VAL = 30
MIN_NODES, MAX_NODES = 3, 6
LINE_THICKNESS_RANGE = (2, 4)

DATA_DIR = os.path.join("dataset")


def random_node_centers(n):
    centers = []
    attempts = 0
    margin = 80
    while len(centers) < n and attempts < n * 30:
        attempts += 1
        cx = random.randint(margin, IMG_W - margin)
        cy = random.randint(margin, IMG_H - margin)
        if all(np.hypot(cx - ox, cy - oy) > 120 for ox, oy in centers):
            centers.append((cx, cy))
    return centers


def draw_node_blob(canvas, cx, cy):
    """Draw a simple placeholder icon blob (rectangle or circle) so lines
    have something visually plausible to connect - the shape itself is
    irrelevant to Intern E's task, only the connecting lines matter."""
    shape = random.choice(["circle", "rect"])
    color = (60, 60, 60)
    if shape == "circle":
        r = random.randint(25, 35)
        cv2.circle(canvas, (cx, cy), r, color, 2)
    else:
        w, h = random.randint(50, 70), random.randint(35, 50)
        cv2.rectangle(canvas, (cx - w // 2, cy - h // 2), (cx + w // 2, cy + h // 2), color, 2)


def draw_edge(canvas, mask, p0, p1, elbow=True):
    thickness = random.randint(*LINE_THICKNESS_RANGE)
    color = (30, 30, 30)
    if elbow and random.random() < 0.5:
        # simple elbow: horizontal then vertical
        mid = (p1[0], p0[1])
        cv2.line(canvas, p0, mid, color, thickness)
        cv2.line(canvas, mid, p1, color, thickness)
        cv2.line(mask, p0, mid, 255, thickness)
        cv2.line(mask, mid, p1, 255, thickness)
    else:
        cv2.line(canvas, p0, p1, color, thickness)
        cv2.line(mask, p0, p1, 255, thickness)


def generate_one(img_id):
    canvas = np.full((IMG_H, IMG_W, 3), 255, dtype=np.uint8)
    mask = np.zeros((IMG_H, IMG_W), dtype=np.uint8)

    n_nodes = random.randint(MIN_NODES, MAX_NODES)
    centers = random_node_centers(n_nodes)

    # random spanning-tree-ish connectivity so the diagram looks plausible
    edges = []
    for i in range(1, len(centers)):
        j = random.randint(0, i - 1)
        edges.append((i, j))
    # a couple of extra random edges
    for _ in range(random.randint(0, 2)):
        if len(centers) >= 2:
            i, j = random.sample(range(len(centers)), 2)
            edges.append((i, j))

    for i, j in edges:
        draw_edge(canvas, mask, centers[i], centers[j])

    for cx, cy in centers:
        draw_node_blob(canvas, cx, cy)

    return canvas, mask


def generate_split(split_name, n_images, start_id=0):
    img_dir = os.path.join(DATA_DIR, "images", split_name)
    mask_dir = os.path.join(DATA_DIR, "masks", split_name)
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(mask_dir, exist_ok=True)

    for i in range(n_images):
        img_id = start_id + i
        canvas, mask = generate_one(img_id)
        name = f"diagram_{img_id:04d}.png"
        cv2.imwrite(os.path.join(img_dir, name), canvas)
        cv2.imwrite(os.path.join(mask_dir, name), mask)
        print(f"[{split_name}] generated {name}")


if __name__ == "__main__":
    random.seed(42)
    generate_split("train", N_TRAIN, start_id=0)
    generate_split("val", N_VAL, start_id=N_TRAIN)
    print(f"\nDone! {N_TRAIN} train / {N_VAL} val image+mask pairs generated in {DATA_DIR}/")
