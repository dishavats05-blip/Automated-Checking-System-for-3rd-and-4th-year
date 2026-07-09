# Intern F - Math & Logic

This folder is the standalone workspace for Track 2, Stream C.

Scope:
- transcribe handwritten math derivations into LaTeX
- parse LaTeX into SymPy expressions
- validate student steps against a reference solution

Suggested layout:
- `src/` for implementation
- `data/` for sample inputs
- `outputs/` for generated results

Quick start:
1. Install dependencies from `requirements.txt`.
2. Run `python src/pipeline.py --help` to see the available commands.
3. Use `python src/pipeline.py transcribe-validate <image_dir> <reference_file>` to run the combined crop-to-validation flow.
