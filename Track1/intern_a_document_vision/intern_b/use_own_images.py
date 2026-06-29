import os
import shutil

# Create directories
os.makedirs(os.path.join("intern_b", "own_dataset", "images"), exist_ok=True)
os.makedirs(os.path.join("intern_b", "own_dataset", "annotations"), exist_ok=True)

# Source directory (use your raw images from input/raw_images)
src_dir = os.path.join("input", "raw_images")

if os.path.exists(src_dir):
    for filename in os.listdir(src_dir):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            # Copy image
            src_path = os.path.join(src_dir, filename)
            dest_img = os.path.join("intern_b", "own_dataset", "images", filename)
            shutil.copy(src_path, dest_img)
            print(f"Copied {filename}")

print("Done! Now your images are in intern_b/own_dataset/images/!")
