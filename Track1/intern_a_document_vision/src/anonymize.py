import cv2
import os

INPUT_DIR = "output/deskewed_images"
OUTPUT_DIR = "output/anonymized_images"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def anonymize_image(image, mask_height=180):
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    height, width = image.shape[:2]
    # Only mask if the image is taller than mask height
    if height > 0:
        cv2.rectangle(image, (0, 0), (width, min(mask_height, height)), (0, 0, 0), -1)
    return image

for file in os.listdir(INPUT_DIR):
    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
        print(f"Anonymizing {file}")
        img = cv2.imread(os.path.join(INPUT_DIR, file))
        if img is not None:
            anonymized = anonymize_image(img)
            cv2.imwrite(os.path.join(OUTPUT_DIR, file), anonymized)

print("Anonymization completed")
