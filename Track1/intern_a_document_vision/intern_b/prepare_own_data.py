import os
import shutil

# Directories
input_images_dir = os.path.join("output", "deskewed_images")
output_images_dir = os.path.join("intern_b", "own_dataset", "images")
os.makedirs(output_images_dir, exist_ok=True)

# Copy images
if os.path.exists(input_images_dir):
    for filename in os.listdir(input_images_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            src = os.path.join(input_images_dir, filename)
            dest = os.path.join(output_images_dir, filename)
            shutil.copy(src, dest)
            print(f"Copied {filename} to own_dataset/images")
    print("\n✅ Images ready for LabelStudio!")
else:
    print("❌ No processed images found!")
