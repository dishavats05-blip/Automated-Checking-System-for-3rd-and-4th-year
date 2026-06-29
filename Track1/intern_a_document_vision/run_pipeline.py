import os
import shutil
import cv2
import numpy as np
import math

INPUT_DIR = "input"
OUTPUT_DIR = "output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Step 1: Load images
print("Step 1: Loading images...")
page_images_dir = os.path.join(OUTPUT_DIR, "page_images")
os.makedirs(page_images_dir, exist_ok=True)

try:
    from pdf2image import convert_from_path
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(INPUT_DIR, filename)
            try:
                pages = convert_from_path(pdf_path)
                for i, page in enumerate(pages):
                    save_path = os.path.join(page_images_dir, f"{os.path.splitext(filename)[0]}_page_{i+1}.png")
                    page.save(save_path, "PNG")
                    print(f"Saved PDF page: {os.path.basename(save_path)}")
            except Exception as e:
                print(f"Skipping PDF {filename}: {e}")
except ImportError:
    print("pdf2image not available, skipping PDF processing")

raw_images_dir = os.path.join(INPUT_DIR, "raw_images")
if os.path.exists(raw_images_dir):
    for filename in os.listdir(raw_images_dir):
        if filename.lower().endswith((".jpeg", ".jpg", ".png")):
            shutil.copy(
                os.path.join(raw_images_dir, filename),
                os.path.join(page_images_dir, filename)
            )
            print(f"Copied raw image: {filename}")

# Step 2: Clean images (color)
print("\nStep 2: Cleaning images...")
cleaned_dir = os.path.join(OUTPUT_DIR, "cleaned_images")
os.makedirs(cleaned_dir, exist_ok=True)

def remove_shadow(image):
    rgb_planes = cv2.split(image)
    result_planes = []
    for plane in rgb_planes:
        dilated_img = cv2.dilate(plane, np.ones((7,7), np.uint8))
        bg_img = cv2.medianBlur(dilated_img, 21)
        diff_img = 255 - cv2.absdiff(plane, bg_img)
        result_planes.append(diff_img)
    return cv2.merge(result_planes)

def clean_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return None
    shadow_removed = remove_shadow(img)
    denoised = cv2.fastNlMeansDenoisingColored(shadow_removed, None, 10, 10, 7, 21)
    return denoised

for file in os.listdir(page_images_dir):
    if file.lower().endswith(('.png','.jpg','.jpeg')):
        print(f"Cleaning {file}...")
        cleaned = clean_image(os.path.join(page_images_dir, file))
        if cleaned is not None:
            cv2.imwrite(os.path.join(cleaned_dir, file), cleaned)
            print(f"Cleaned {file} saved")

# Step 3: Deskew AND Crop tightly!
print("\nStep 3: Deskewing and cropping images...")
deskewed_dir = os.path.join(OUTPUT_DIR, "deskewed_images")
os.makedirs(deskewed_dir, exist_ok=True)

def get_skew_angle(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30,5))
    dilated = cv2.dilate(thresh, kernel, iterations=2)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    angles = []
    if contours:
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
        for cnt in contours:
            rect = cv2.minAreaRect(cnt)
            angle = rect[-1]
            if angle < -45:
                angle +=90
            elif angle >45:
                angle -=90
            angles.append(angle)
    
    if len(angles) < 2:
        edges = cv2.Canny(gray,50,150,apertureSize=3)
        lines = cv2.HoughLinesP(edges,1,np.pi/180,50,100,20)
        if lines is not None:
            for line in lines:
                x1,y1,x2,y2 = line[0]
                angle = math.degrees(math.atan2(y2-y1, x2-x1))
                if -45 <= angle <=45:
                    angles.append(angle)
                elif angle>45:
                    angles.append(angle-90)
                elif angle < -45:
                    angles.append(angle+90)
    
    if len(angles) ==0:
        return 0.0
    return round(np.median(angles),1)

def crop_to_content(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray,240,255,cv2.THRESH_BINARY_INV)
    coords = cv2.findNonZero(thresh)
    if coords is None:
        return image
    x,y,w,h = cv2.boundingRect(coords)
    padding =10
    x,y = max(0,x-padding), max(0,y-padding)
    w = min(image.shape[1]-x, w+2*padding)
    h = min(image.shape[0]-y, h+2*padding)
    return image[y:y+h, x:x+w]

def deskew_and_crop(image):
    skew_angle = get_skew_angle(image)
    print(f"Detected skew angle: {skew_angle} degrees")
    
    h_full, w_full = image.shape[:2]
    center = (w_full//2, h_full//2)
    M = cv2.getRotationMatrix2D(center, skew_angle, 1.0)
    cos = np.abs(M[0,0])
    sin = np.abs(M[0,1])
    new_w = int((h_full*sin)+(w_full*cos))
    new_h = int((h_full*cos)+(w_full*sin))
    
    M[0,2] += (new_w/2)-center[0]
    M[1,2] += (new_h/2)-center[1]
    
    rotated = cv2.warpAffine(
        image, M, (new_w, new_h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255,255,255)
    )
    
    return crop_to_content(rotated)

for file in os.listdir(cleaned_dir):
    if file.lower().endswith(('.png','.jpg','.jpeg')):
        print(f"Deskewing and cropping {file}...")
        img = cv2.imread(os.path.join(cleaned_dir, file))
        if img is not None:
            result = deskew_and_crop(img)
            cv2.imwrite(os.path.join(deskewed_dir, file), result)
            print(f"Saved {file}")

# Step4: Anonymize
print("\nStep4: Anonymizing images...")
anonymized_dir = os.path.join(OUTPUT_DIR, "anonymized_images")
os.makedirs(anonymized_dir, exist_ok=True)

def anonymize_image(image, mask_height=180):
    if len(image.shape) ==2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    h,w = image.shape[:2]
    if h>0:
        cv2.rectangle(image, (0,0), (w, min(mask_height, h)), (0,0,0), -1)
    return image

for file in os.listdir(deskewed_dir):
    if file.lower().endswith(('.png','.jpg','.jpeg')):
        print(f"Anonymizing {file}...")
        img = cv2.imread(os.path.join(deskewed_dir, file))
        if img is not None:
            anonymized = anonymize_image(img)
            cv2.imwrite(os.path.join(anonymized_dir, file), anonymized)
            print(f"Anonymized {file} saved")

print("\nAll steps completed!")
