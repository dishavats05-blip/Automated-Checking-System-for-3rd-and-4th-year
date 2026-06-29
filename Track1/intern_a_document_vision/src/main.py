import os
import subprocess
import sys

def run_script(script_name):
    script_path = os.path.join("src", script_name)
    print(f"Running {script_name}...")
    result = subprocess.run([sys.executable, script_path])
    if result.returncode != 0:
        print(f"Error running {script_name}")
        sys.exit(1)

def main():
    run_script("pdf_to_image.py")
    run_script("image_cleaning.py")
    run_script("deskew.py")
    run_script("anonymize.py")
    print("Pipeline Finished Successfully")

if __name__ == "__main__":
    main()
