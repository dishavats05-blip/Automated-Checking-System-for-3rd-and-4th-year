import os
import random
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Create dummy data directory
os.makedirs(os.path.join("intern_b", "dataset", "images"), exist_ok=True)
os.makedirs(os.path.join("intern_b", "dataset", "annotations"), exist_ok=True)

COLORS = {
    "PROSE_TEXT": (50, 50, 50),
    "CODE_CANVAS": (200, 200, 200),
    "DIAGRAM_REGION": (180, 220, 255),
    "MATH_DERIVATION": (255, 220, 180),
}

LABELS = list(COLORS.keys())

def generate_text_block(draw, start_x, start_y, width, block_type):
    if block_type == "PROSE_TEXT":
        # Draw lines of text
        line_height = random.randint(15, 25)
        current_y = start_y
        while current_y + line_height < start_y + random.randint(80, 200):
            line_width = random.randint(int(width*0.6), width-20)
            draw.rectangle([(start_x+10, current_y), (start_x+10+line_width, current_y+line_height-5)], fill=COLORS[block_type])
            current_y += line_height + 5
        return current_y - start_y
    elif block_type == "CODE_CANVAS":
        # Draw code-like blocks
        block_h = random.randint(100, 250)
        draw.rectangle([(start_x, start_y), (start_x+width-10, start_y+block_h)], fill=COLORS[block_type], outline=(100,100,100), width=2)
        # Add code lines
        line_y = start_y + 10
        for _ in range(random.randint(5, 15)):
            line_w = random.randint(int(width*0.3), width-30)
            draw.rectangle([(start_x+15, line_y), (start_x+15+line_w, line_y+8)], fill=(80,80,80))
            line_y += random.randint(12, 20)
        return block_h
    elif block_type == "DIAGRAM_REGION":
        # Draw diagram
        block_h = random.randint(120, 220)
        draw.rectangle([(start_x, start_y), (start_x+width-10, start_y+block_h)], fill=COLORS[block_type], outline=(100,150,200), width=2)
        # Add some shapes
        center_x = start_x + (width-10)//2
        center_y = start_y + block_h//2
        draw.ellipse([(center_x-30, center_y-30), (center_x+30, center_y+30)], outline=(100,150,200), width=3)
        draw.line([(center_x, center_y-30), (center_x, center_y-60)], fill=(100,150,200), width=3)
        draw.line([(center_x, center_y+30), (center_x, center_y+60)], fill=(100,150,200), width=3)
        draw.line([(center_x-30, center_y), (center_x-60, center_y)], fill=(100,150,200), width=3)
        draw.line([(center_x+30, center_y), (center_x+60, center_y)], fill=(100,150,200), width=3)
        return block_h
    elif block_type == "MATH_DERIVATION":
        # Draw math-like blocks
        block_h = random.randint(90, 180)
        draw.rectangle([(start_x, start_y), (start_x+width-10, start_y+block_h)], fill=COLORS[block_type], outline=(200,150,100), width=2)
        # Add math symbols
        line_y = start_y + 15
        for _ in range(random.randint(3, 8)):
            draw.rectangle([(start_x+20, line_y), (start_x+width-30, line_y+10)], fill=(150,100,50))
            line_y += random.randint(18, 28)
        return block_h

def generate_dummy_image(img_id, img_width=800, img_height=1000):
    # Create white background
    img = Image.new("RGB", (img_width, img_height), color=(255,255,255))
    draw = ImageDraw.Draw(img)
    
    annotations = []
    current_y = 50
    
    # Add random blocks
    num_blocks = random.randint(3, 7)
    for _ in range(num_blocks):
        block_type = random.choice(LABELS)
        block_x = 50
        block_height = generate_text_block(draw, block_x, current_y, img_width-100, block_type)
        # Save annotation
        annotations.append({
            "label": block_type,
            "bbox": [block_x, current_y, img_width-50, current_y + block_height]
        })
        current_y += block_height + 40
        if current_y > img_height - 100:
            break
    
    # Save image
    img_path = os.path.join("intern_b", "dataset", "images", f"dummy_{img_id:03d}.png")
    img.save(img_path)
    
    # Save annotations (JSON)
    import json
    ann_path = os.path.join("intern_b", "dataset", "annotations", f"dummy_{img_id:03d}.json")
    with open(ann_path, "w") as f:
        json.dump({
            "image_id": img_id,
            "image_path": img_path,
            "width": img_width,
            "height": img_height,
            "annotations": annotations
        }, f, indent=2)
    
    print(f"Generated dummy_{img_id:03d}")

# Generate 200 dummy images
for i in range(1, 201):
    generate_dummy_image(i)
print("Done generating 200 dummy images!")
