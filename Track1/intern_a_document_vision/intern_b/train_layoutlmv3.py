import os
import json
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    LayoutLMv3ForTokenClassification,
    LayoutLMv3Processor,
    TrainingArguments,
    Trainer
)
from PIL import Image
import numpy as np

# Configuration
MODEL_NAME = "microsoft/layoutlmv3-base"
OUTPUT_DIR = os.path.join("intern_b", "model")
DATA_DIR = os.path.join("intern_b", "dataset")
LABELS = ["PROSE_TEXT", "CODE_CANVAS", "DIAGRAM_REGION", "MATH_DERIVATION"]
id2label = {k: v for k, v in enumerate(LABELS)}
label2id = {v: k for k, v in enumerate(LABELS)}


class DummyLayoutDataset(Dataset):
    def __init__(self, data_dir, processor, split="train"):
        self.data_dir = data_dir
        self.processor = processor
        self.image_dir = os.path.join(data_dir, "images")
        self.ann_dir = os.path.join(data_dir, "annotations")
        
        # Get all files
        self.files = [f for f in os.listdir(self.image_dir) if f.endswith(".png")]
        # Split into train/val (80/20)
        split_idx = int(0.8 * len(self.files))
        if split == "train":
            self.files = self.files[:split_idx]
        else:
            self.files = self.files[split_idx:]
    
    def __len__(self):
        return len(self.files)
    
    def __getitem__(self, idx):
        img_file = self.files[idx]
        img_path = os.path.join(self.image_dir, img_file)
        ann_path = os.path.join(self.ann_dir, img_file.replace(".png", ".json"))
        
        # Load image and annotations
        image = Image.open(img_path).convert("RGB")
        with open(ann_path, "r") as f:
            ann = json.load(f)
        
        # Create boxes and labels for layoutlmv3 (we'll simulate word-level annotations)
        words = []
        boxes = []
        labels = []
        
        for obj in ann["annotations"]:
            # For dummy data, we'll treat each object as a single "word" with its bbox
            words.append("DUMMY")
            # LayoutLMv3 expects boxes in [x0, y0, x1, y1] format, normalized to 0-1000
            x0, y0, x1, y1 = obj["bbox"]
            width, height = ann["width"], ann["height"]
            normalized_box = [
                int((x0 / width) * 1000),
                int((y0 / height) * 1000),
                int((x1 / width) * 1000),
                int((y1 / height) * 1000)
            ]
            boxes.append(normalized_box)
            labels.append(label2id[obj["label"]])
        
        # Process using LayoutLMv3 processor
        encoding = self.processor(
            image, 
            words, 
            boxes=boxes, 
            word_labels=labels,
            return_tensors="pt",
            truncation=True,
            padding="max_length",
            max_length=512
        )
        
        # Remove batch dimension
        for k, v in encoding.items():
            encoding[k] = v.squeeze()
        
        return encoding


def main():
    print("Loading processor and model...")
    processor = LayoutLMv3Processor.from_pretrained(MODEL_NAME, apply_ocr=False)
    model = LayoutLMv3ForTokenClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(LABELS),
        id2label=id2label,
        label2id=label2id
    )
    
    print("Loading datasets...")
    train_dataset = DummyLayoutDataset(DATA_DIR, processor, split="train")
    val_dataset = DummyLayoutDataset(DATA_DIR, processor, split="val")
    
    print("Setting up training arguments...")
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        num_train_epochs=3,
        learning_rate=5e-5,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        logging_steps=10,
    )
    
    def compute_metrics(eval_pred):
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=2)
        
        # Calculate accuracy (ignoring padding)
        true_predictions = []
        true_labels = []
        for prediction, label in zip(predictions, labels):
            for pred, lab in zip(prediction, label):
                if lab != -100:
                    true_predictions.append(pred)
                    true_labels.append(lab)
        
        accuracy = np.mean(np.array(true_predictions) == np.array(true_labels))
        return {"accuracy": accuracy}
    
    print("Initializing trainer...")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
    )
    
    print("Starting training...")
    trainer.train()
    
    print("Saving model and processor...")
    model.save_pretrained(OUTPUT_DIR)
    processor.save_pretrained(OUTPUT_DIR)
    
    print("Done!")


if __name__ == "__main__":
    main()
