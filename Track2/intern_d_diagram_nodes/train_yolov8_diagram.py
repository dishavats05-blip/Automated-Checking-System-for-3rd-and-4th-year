"""
Intern D - Stream B (Diagram Nodes)
Fine-tunes YOLOv8-obb to detect and classify hand-drawn networking icons
(Router / Switch / Firewall / Server) inside DIAGRAM_REGION crops.

Requires: pip install ultralytics
Data:     run generate_dummy_diagram_data.py first (or point --data at a
          dataset.yaml built from real annotations via
          convert_labelstudio_to_obb.py).

Usage:
    python train_yolov8_diagram.py
    python train_yolov8_diagram.py --epochs 100 --model yolov8s-obb.pt
"""

import argparse
import os

from ultralytics import YOLO

MODEL_OUT_DIR = os.path.join("model")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="dataset.yaml", help="Path to dataset.yaml")
    parser.add_argument("--model", default="yolov8n-obb.pt",
                         help="Base YOLOv8-obb checkpoint to fine-tune from")
    parser.add_argument("--epochs", type=int, default=60)
    parser.add_argument("--imgsz", type=int, default=800)
    parser.add_argument("--batch", type=int, default=8)
    args = parser.parse_args()

    print(f"Loading base model {args.model}...")
    model = YOLO(args.model)

    print("Starting training...")
    results = model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        project=MODEL_OUT_DIR,
        name="diagram_nodes",
        exist_ok=True,
    )

    best_weights = os.path.join(MODEL_OUT_DIR, "diagram_nodes", "weights", "best.pt")
    print(f"\nDone! Best weights saved to {best_weights}")
    print("Point infer_diagram_nodes.py --weights at this file to run inference.")


if __name__ == "__main__":
    main()
