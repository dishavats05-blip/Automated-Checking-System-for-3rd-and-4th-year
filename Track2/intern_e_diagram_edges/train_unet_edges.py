"""
Intern E - Stream B (Diagram Edges)
Trains a thin U-Net++ (small encoder, binary output) to segment connector
lines out of DIAGRAM_REGION crops. The predicted mask is later
skeletonized and Hough-parsed (see infer_diagram_edges.py) to recover
individual edge endpoints.

Requires: pip install torch segmentation-models-pytorch albumentations
Data:     run generate_dummy_edge_data.py first.

Usage:
    python train_unet_edges.py --epochs 25
"""

import argparse
import os

import cv2
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import segmentation_models_pytorch as smp

DATA_DIR = os.path.join("dataset")
MODEL_OUT_DIR = os.path.join("model")
IMG_SIZE = 512


class EdgeMaskDataset(Dataset):
    def __init__(self, split):
        self.img_dir = os.path.join(DATA_DIR, "images", split)
        self.mask_dir = os.path.join(DATA_DIR, "masks", split)
        self.files = sorted(f for f in os.listdir(self.img_dir) if f.endswith(".png"))

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        name = self.files[idx]
        img = cv2.imread(os.path.join(self.img_dir, name), cv2.IMREAD_COLOR)
        mask = cv2.imread(os.path.join(self.mask_dir, name), cv2.IMREAD_GRAYSCALE)

        img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
        mask = cv2.resize(mask, (IMG_SIZE, IMG_SIZE), interpolation=cv2.INTER_NEAREST)

        img = img.astype(np.float32) / 255.0
        img = np.transpose(img, (2, 0, 1))  # HWC -> CHW
        mask = (mask.astype(np.float32) / 255.0)[None, ...]  # 1xHxW

        return torch.from_numpy(img), torch.from_numpy(mask)


def dice_loss(pred, target, eps=1e-6):
    pred = torch.sigmoid(pred)
    intersection = (pred * target).sum(dim=(1, 2, 3))
    union = pred.sum(dim=(1, 2, 3)) + target.sum(dim=(1, 2, 3))
    dice = (2 * intersection + eps) / (union + eps)
    return 1 - dice.mean()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--batch_size", type=int, default=8)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--encoder", default="mobilenet_v2",
                         help="Lightweight encoder to keep the model 'thin'")
    args = parser.parse_args()

    os.makedirs(MODEL_OUT_DIR, exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    model = smp.UnetPlusPlus(
        encoder_name=args.encoder,
        encoder_weights="imagenet",
        in_channels=3,
        classes=1,
    ).to(device)

    train_ds = EdgeMaskDataset("train")
    val_ds = EdgeMaskDataset("val")
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, num_workers=2)

    bce = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    best_val_loss = float("inf")
    for epoch in range(1, args.epochs + 1):
        model.train()
        train_loss = 0.0
        for imgs, masks in train_loader:
            imgs, masks = imgs.to(device), masks.to(device)
            optimizer.zero_grad()
            logits = model(imgs)
            loss = bce(logits, masks) + dice_loss(logits, masks)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * imgs.size(0)
        train_loss /= len(train_ds)

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for imgs, masks in val_loader:
                imgs, masks = imgs.to(device), masks.to(device)
                logits = model(imgs)
                loss = bce(logits, masks) + dice_loss(logits, masks)
                val_loss += loss.item() * imgs.size(0)
        val_loss /= max(1, len(val_ds))

        print(f"Epoch {epoch}/{args.epochs}  train_loss={train_loss:.4f}  val_loss={val_loss:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), os.path.join(MODEL_OUT_DIR, "unet_edges_best.pt"))
            print(f"  -> new best model saved (val_loss={val_loss:.4f})")

    print(f"\nDone! Best weights saved to {os.path.join(MODEL_OUT_DIR, 'unet_edges_best.pt')}")


if __name__ == "__main__":
    main()
