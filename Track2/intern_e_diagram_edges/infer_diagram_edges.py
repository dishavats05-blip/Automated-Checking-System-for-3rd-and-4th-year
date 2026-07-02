"""
Intern E - Stream B (Diagram Edges)
Full inference pipeline for connector-line extraction:

    1. Run the trained U-Net++ over a DIAGRAM_REGION crop -> probability
       mask of "line" pixels.
    2. Threshold to a binary mask.
    3. Skeletonize (skimage) to condense thick, noisy strokes down to
       single-pixel-wide tracks.
    4. Run a probabilistic Hough transform over the skeleton to recover
       each line segment's terminal (start, end) coordinates.

Output format (per image), matching the spec exactly:
    [((x0, y0), (x1, y1)), ...]
(JSON has no tuple type, so this is serialized as a list of 2-point lists:
    [[[x0, y0], [x1, y1]], ...]
 - reconstruct tuples on load with: [tuple(map(tuple, e)) for e in data])

Requires: pip install torch segmentation-models-pytorch scikit-image opencv-python
Usage:
    python infer_diagram_edges.py --weights model/unet_edges_best.pt
"""

import argparse
import json
import os

import cv2
import numpy as np
from skimage.morphology import skeletonize

DEFAULT_INPUT_DIR = os.path.join(
    "..", "..", "Track1", "intern_a_document_vision", "local_storage", "extracted_crops"
)
DEFAULT_OUTPUT_DIR = os.path.join("..", "local_storage", "diagram_edges")
IMG_SIZE = 512


def is_diagram_crop(filename):
    return "DIAGRAM_REGION" in filename.upper() and filename.lower().endswith(
        (".png", ".jpg", ".jpeg")
    )


def load_model(weights_path, encoder):
    import torch
    import segmentation_models_pytorch as smp

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = smp.UnetPlusPlus(
        encoder_name=encoder, encoder_weights=None, in_channels=3, classes=1,
    )
    model.load_state_dict(torch.load(weights_path, map_location=device))
    model.to(device).eval()
    return model, device


def predict_mask(model, device, image_bgr, mask_thresh=0.5):
    import torch

    orig_h, orig_w = image_bgr.shape[:2]
    resized = cv2.resize(image_bgr, (IMG_SIZE, IMG_SIZE))
    x = resized.astype(np.float32) / 255.0
    x = np.transpose(x, (2, 0, 1))[None, ...]
    x = torch.from_numpy(x).to(device)

    with torch.no_grad():
        logits = model(x)
        prob = torch.sigmoid(logits)[0, 0].cpu().numpy()

    mask = (prob > mask_thresh).astype(np.uint8) * 255
    mask = cv2.resize(mask, (orig_w, orig_h), interpolation=cv2.INTER_NEAREST)
    return mask


def mask_to_edges(binary_mask, hough_threshold=30, min_line_length=20, max_line_gap=8):
    """Skeletonize the binary line mask, then run a probabilistic Hough
    transform to recover terminal (start, end) coordinates of each link."""
    skeleton = skeletonize(binary_mask > 0)
    skeleton_uint8 = (skeleton.astype(np.uint8)) * 255

    lines = cv2.HoughLinesP(
        skeleton_uint8,
        rho=1,
        theta=np.pi / 180,
        threshold=hough_threshold,
        minLineLength=min_line_length,
        maxLineGap=max_line_gap,
    )

    edges = []
    if lines is not None:
        for line in lines:
            x0, y0, x1, y1 = line[0]
            edges.append(((int(x0), int(y0)), (int(x1), int(y1))))
    return edges, skeleton_uint8


def process_image(model, device, image_path):
    image = cv2.imread(image_path)
    if image is None:
        return []
    mask = predict_mask(model, device, image)
    edges, _ = mask_to_edges(mask)
    return edges


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights", required=True, help="Path to trained unet_edges_best.pt")
    parser.add_argument("--encoder", default="mobilenet_v2",
                         help="Must match the encoder used in train_unet_edges.py")
    parser.add_argument("--input_dir", default=DEFAULT_INPUT_DIR,
                         help="Directory of DIAGRAM_REGION crops")
    parser.add_argument("--output_dir", default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    print(f"Loading model from {args.weights}...")
    model, device = load_model(args.weights, args.encoder)

    if not os.path.exists(args.input_dir):
        print(f"ERROR: input dir not found: {args.input_dir}")
        return

    all_results = {}
    for filename in sorted(os.listdir(args.input_dir)):
        if not is_diagram_crop(filename):
            continue
        image_path = os.path.join(args.input_dir, filename)
        print(f"Processing {filename}...")
        edges = process_image(model, device, image_path)
        all_results[filename] = edges

        per_image_path = os.path.join(
            args.output_dir, os.path.splitext(filename)[0] + "_edges.json"
        )
        with open(per_image_path, "w") as f:
            json.dump(edges, f, indent=2)
        print(f"  -> {len(edges)} edge(s) found, saved to {per_image_path}")

    combined_path = os.path.join(args.output_dir, "diagram_edges_results.json")
    with open(combined_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nDone! Combined results saved to {combined_path}")


if __name__ == "__main__":
    main()
