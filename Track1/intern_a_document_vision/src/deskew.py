import cv2
import numpy as np
import os
import math

INPUT_DIR = "output/cleaned_images"
OUTPUT_DIR = "output/deskewed_images"

os.makedirs(OUTPUT_DIR, exist_ok=True)

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
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=100, maxLineGap=20)
        if lines is not None:
            for line in lines:
                x1,y1,x2,y2 = line[0]
                angle = math.degrees(math.atan2(y2-y1, x2-x1))
                if -45 <= angle <=45:
                    angles.append(angle)
                elif angle >45:
                    angles.append(angle-90)
                elif angle < -45:
                    angles.append(angle+90)
    
    if len(angles) ==0:
        return 0.0
    return round(np.median(angles),1)

def crop_to_content(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    coords = cv2.findNonZero(thresh)
    if coords is None:
        return image
    x, y, w, h = cv2.boundingRect(coords)
    padding = 10
    x = max(0, x - padding)
    y = max(0, y - padding)
    w = min(image.shape[1] - x, w + 2*padding)
    h = min(image.shape[0] - y, h + 2*padding)
    return image[y:y+h, x:x+w]

def deskew_and_crop(image):
    skew_angle = get_skew_angle(image)
    print(f"Detected skew angle: {skew_angle} degrees")
    
    h_full, w_full = image.shape[:2]
    center = (w_full//2, h_full//2)
    
    M = cv2.getRotationMatrix2D(center, skew_angle, 1.0)
    
    cos = np.abs(M[0,0])
    sin = np.abs(M[0,1])
    new_w = int((h_full * sin) + (w_full * cos))
    new_h = int((h_full * cos) + (w_full * sin))
    
    M[0, 2] += (new_w / 2) - center[0]
    M[1, 2] += (new_h / 2) - center[1]
    
    rotated = cv2.warpAffine(
        image, M, (new_w, new_h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255,255,255)
    )
    
    return crop_to_content(rotated)

for file in os.listdir(INPUT_DIR):
    if file.lower().endswith(('.png','.jpg','.jpeg')):
        print(f"Processing {file}")
        img = cv2.imread(os.path.join(INPUT_DIR, file))
        if img is not None:
            result = deskew_and_crop(img)
            cv2.imwrite(os.path.join(OUTPUT_DIR, file), result)

print("Deskew and crop completed!")
