import os
import json
import cv2

# Directories
images_dir = os.path.join("intern_b", "own_dataset", "images")
# Use the actual annotations file you have
annotations_path = os.path.join("intern_b", "own_dataset", "annotations.json")
output_dir = os.path.join("local_storage", "extracted_crops")

os.makedirs(output_dir, exist_ok=True)

# Check if annotations file exists
if not os.path.exists(annotations_path):
    print(f"ERROR: Annotations file not found at {annotations_path}")
    print("Please update the 'annotations_path' variable to point to your LabelStudio export file!")
    exit()

# Load annotations
with open(annotations_path, "r", encoding="utf-8") as f:
    annotations = json.load(f)

# Get list of your actual image files to match
actual_images = [f for f in os.listdir(images_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

# Process each annotated image
for item in annotations:
    # Get image path from LabelStudio
    ls_image_path = item["data"]["image"]
    # Extract filename and remove LabelStudio prefix (like "e2bb3a14-")
    ls_filename = os.path.basename(ls_image_path)
    # Try to match with your actual images - handle space vs underscore
    image_name = None
    # Normalize both filenames (replace underscores/spaces, make lowercase)
    ls_normalized = ls_filename.lower().replace("_", " ").replace("-", " ")
    for actual_img in actual_images:
        actual_normalized = actual_img.lower().replace("_", " ").replace("-", " ")
        if actual_normalized in ls_normalized or ls_normalized.endswith(actual_normalized):
            image_name = actual_img
            break
    if image_name is None:
        print(f"Warning: Could not find matching image for {ls_filename}, skipping...")
        continue
    
    image_path = os.path.join(images_dir, image_name)

    if not os.path.exists(image_path):
        print(f"Warning: Image {image_name} not found, skipping...")
        continue

    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Warning: Could not read image {image_name}, skipping...")
        continue

    # Get image dimensions
    img_height, img_width = img.shape[:2]

    # Process each annotation (bounding box)
    for idx, annotation in enumerate(item.get("annotations", [{}])[0].get("result", [])):
        # Get label and bounding box coordinates
        label = annotation["value"]["rectanglelabels"][0]
        # Convert percentages to pixels (LabelStudio uses % of image size)
        x = int((annotation["value"]["x"] / 100) * img_width)
        y = int((annotation["value"]["y"] / 100) * img_height)
        w = int((annotation["value"]["width"] / 100) * img_width)
        h = int((annotation["value"]["height"] / 100) * img_height)

        # Crop the region
        cropped_img = img[y:y+h, x:x+w]

        # Save the cropped image
        base_name = os.path.splitext(image_name)[0]
        crop_filename = f"{base_name}_{label}_{idx+1}.jpg"
        crop_path = os.path.join(output_dir, crop_filename)
        cv2.imwrite(crop_path, cropped_img)
        print(f"Saved crop: {crop_filename}")

print("\nDone! All crops saved to local_storage/extracted_crops/")
