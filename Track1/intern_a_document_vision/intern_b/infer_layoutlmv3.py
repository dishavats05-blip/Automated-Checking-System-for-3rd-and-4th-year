import os
import json
from PIL import Image

# Configuration
OUTPUT_CROPS_DIR = os.path.join("local_storage", "extracted_crops")
os.makedirs(OUTPUT_CROPS_DIR, exist_ok=True)


def process_image_with_annotations(image_path):
    # Load image
    image = Image.open(image_path).convert("RGB")
    
    # Load dummy annotations
    ann_path = image_path.replace("images", "annotations").replace(".png", ".json")
    with open(ann_path, "r") as f:
        ann_data = json.load(f)
    
    return image, ann_data


def save_crops(image, ann_data, img_name):
    results = []
    for i, obj in enumerate(ann_data["annotations"]):
        label = obj["label"]
        x0, y0, x1, y1 = obj["bbox"]
        # Crop
        crop = image.crop((x0, y0, x1, y1))
        # Save crop
        crop_filename = f"{os.path.splitext(img_name)[0]}_{label}_{i:02d}.png"
        crop_path = os.path.join(OUTPUT_CROPS_DIR, crop_filename)
        crop.save(crop_path)
        # Add to results
        results.append({
            "label": label,
            "bbox": [x0, y0, x1, y1],
            "crop_path": crop_path
        })
        print(f"Saved crop: {crop_filename}")
    return results


def main(input_dir=None):
    # Process images
    if input_dir is None:
        input_dir = os.path.join("intern_b", "dataset", "images")
    
    all_results = []
    # Just process first 5 images for demo
    for idx, filename in enumerate(os.listdir(input_dir)):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')) and idx < 5:
            print(f"\nProcessing {filename}...")
            img_path = os.path.join(input_dir, filename)
            image, ann_data = process_image_with_annotations(img_path)
            results = save_crops(image, ann_data, filename)
            all_results.append({
                "image": filename,
                "detections": results
            })
    
    # Save all results
    results_path = os.path.join("local_storage", "detection_results.json")
    with open(results_path, "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nDone! Results saved to {results_path}")


if __name__ == "__main__":
    main()
