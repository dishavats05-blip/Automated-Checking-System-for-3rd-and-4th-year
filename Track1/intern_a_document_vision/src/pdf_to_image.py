import os
import shutil

INPUT_DIR = "input"
OUTPUT_DIR = "output/page_images"

os.makedirs(OUTPUT_DIR, exist_ok=True)

try:
    from pdf2image import convert_from_path
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(INPUT_DIR, filename)
            try:
                pages = convert_from_path(pdf_path)
                for i, page in enumerate(pages):
                    page.save(os.path.join(OUTPUT_DIR, f"{os.path.splitext(filename)[0]}_page_{i+1}.png"), "PNG")
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
                os.path.join(OUTPUT_DIR, filename)
            )

print("Image processing completed")
