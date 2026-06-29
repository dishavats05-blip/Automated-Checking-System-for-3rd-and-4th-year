import cv2
import numpy as np
from skimage.filters import threshold_sauvola

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
        print("Could not read image")
        return None
    print("Image read successfully")
    shadow_removed = remove_shadow(img)
    print("Shadow removed")
    gray = cv2.cvtColor(shadow_removed, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    window_size = 25
    sauvola_thresh = threshold_sauvola(denoised, window_size=window_size)
    binary = denoised > sauvola_thresh
    binary = (binary * 255).astype(np.uint8)
    return binary

test_img = "output/page_images/WhatsApp Image 2026-06-12 at 14.19.42.jpeg"
cleaned = clean_image(test_img)
if cleaned is not None:
    cv2.imwrite("test_cleaned.jpg", cleaned)
    print("Saved test_cleaned.jpg")
