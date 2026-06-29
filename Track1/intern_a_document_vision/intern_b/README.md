# Intern B - Layout Segmentation

## Overview
This directory contains code for layout segmentation using microsoft/layoutlmv3-base.

## Tasks Implemented

### 1. Generate Dummy Dataset
We generated 200 dummy script images with mixed content types (text, code, diagrams, math).

```bash
python intern_b/generate_dummy_data.py
```

Images saved to `intern_b/dataset/images/`, annotations to `intern_b/dataset/annotations/`

### 2. LabelStudio Configuration
To annotate real data, use the LabelStudio config in `intern_b/labelstudio_config.xml`

### 3. Fine-Tune LayoutLMv3
```bash
python intern_b/train_layoutlmv3.py
```
Model and processor saved to `intern_b/model/`

### 4. Run Inference & Extract Crops
```bash
python intern_b/infer_layoutlmv3.py
```
Crops saved to `local_storage/extracted_crops/`, results to `local_storage/detection_results.json`
