import os
import cv2
import numpy as np

INPUT_DIR = "output/page_images"
OUTPUT_DIR = "output/cleaned_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def remove_shadow(image):
    rgb_planes = cv2.split(image)
    result_planes = []
    for plane in rgb_planes:
        dilated_img = cv2.dilate(plane, np.ones((7,7), np.uint8))
        bg_img = cv2.medianBlur(dilated_img, 21)
        diff_img = 255 - cv2.absdiff(plane, bg_img)
        result_planes.append(diff_img)
    result = cv2.merge(result_planes)
    return result

def clean_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Could not read {image_path}")
        return None
    shadow_removed = remove_shadow(img)
    denoised = cv2.fastNlMeansDenoisingColored(shadow_removed, None, 10, 10, 7, 21)
    return denoised

for file in os.listdir(INPUT_DIR):
    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
        print(f"Processing {file}")
        cleaned = clean_image(os.path.join(INPUT_DIR, file))
        if cleaned is not None:
            cv2.imwrite(os.path.join(OUTPUT_DIR, file), cleaned)
            print(f"Saved {file}")

print("Cleaning completed")
