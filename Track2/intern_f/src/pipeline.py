from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import CONFIG
from src.donut_transcriber import DonutMathTranscriber, transcribe_math_directory
from src.equation_validator import validate_step_sequence


def load_lines(path: Path) -> List[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def cmd_transcribe(image_path: str) -> None:
    transcriber = DonutMathTranscriber()
    result = transcriber.transcribe_image(image_path)
    print(json.dumps({"latex": result.latex, "source": result.source}, indent=2))


def cmd_transcribe_dir(image_dir: str, output_path: str | None) -> None:
    results = transcribe_math_directory(image_dir)
    payload = [result.__dict__ for result in results]

    write_json_output(payload, output_path, "math_transcriptions.json")

    print(json.dumps(payload, indent=2))


def collect_math_transcriptions(image_dir: str | Path, transcriber: DonutMathTranscriber | None = None):
    directory = Path(image_dir)
    active_transcriber = transcriber or DonutMathTranscriber()
    results = []

    for image_path in sorted(directory.iterdir()):
        if image_path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            continue
        results.append(active_transcriber.transcribe_image(image_path))

    return results


def transcribe_and_validate_directory(
    image_dir: str | Path,
    reference_file: str | Path,
    transcriber: DonutMathTranscriber | None = None,
):
    transcriptions = collect_math_transcriptions(image_dir, transcriber)
    reference_steps = load_lines(Path(reference_file))
    validation_results = validate_step_sequence([result.latex for result in transcriptions], reference_steps)

    return {
        "transcriptions": [result.__dict__ for result in transcriptions],
        "validation_results": [result.__dict__ for result in validation_results],
    }


def cmd_transcribe_validate(image_dir: str, reference_file: str, output_path: str | None) -> None:
    payload = transcribe_and_validate_directory(image_dir, reference_file)

    write_json_output(payload, output_path, "transcribe_validate_results.json")
    print(json.dumps(payload, indent=2))


def cmd_validate(student_file: str, reference_file: str) -> None:
    student_steps = load_lines(Path(student_file))
    reference_steps = load_lines(Path(reference_file))
    results = validate_step_sequence(student_steps, reference_steps)
    payload = [result.__dict__ for result in results]
    print(json.dumps(payload, indent=2))


def cmd_validate_with_output(student_file: str, reference_file: str, output_path: str | None) -> None:
    student_steps = load_lines(Path(student_file))
    reference_steps = load_lines(Path(reference_file))
    results = validate_step_sequence(student_steps, reference_steps)
    payload = [result.__dict__ for result in results]

    write_json_output(payload, output_path, "validation_results.json")
    print(json.dumps(payload, indent=2))


def write_json_output(payload: object, output_path: str | None, default_filename: str) -> Path:
    target_path = Path(output_path) if output_path is not None else CONFIG.outputs_dir / default_filename
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return target_path


def cmd_demo() -> None:
    examples_dir = CONFIG.project_root / "examples"
    student_file = examples_dir / "student_steps.txt"
    reference_file = examples_dir / "reference_steps.txt"

    if not student_file.exists() or not reference_file.exists():
        raise FileNotFoundError("Expected examples/student_steps.txt and examples/reference_steps.txt")

    cmd_validate(str(student_file), str(reference_file))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Intern F math and logic pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    transcribe_parser = subparsers.add_parser("transcribe", help="Transcribe a handwritten math image")
    transcribe_parser.add_argument("image_path")

    transcribe_dir_parser = subparsers.add_parser("transcribe-dir", help="Transcribe all math images in a folder")
    transcribe_dir_parser.add_argument("image_dir")
    transcribe_dir_parser.add_argument("--output", dest="output_path")

    transcribe_validate_parser = subparsers.add_parser(
        "transcribe-validate",
        help="Transcribe math images and validate them against a reference step file",
    )
    transcribe_validate_parser.add_argument("image_dir")
    transcribe_validate_parser.add_argument("reference_file")
    transcribe_validate_parser.add_argument("--output", dest="output_path")

    validate_parser = subparsers.add_parser("validate", help="Validate student and reference LaTeX steps")
    validate_parser.add_argument("student_file")
    validate_parser.add_argument("reference_file")
    validate_parser.add_argument("--output", dest="output_path")

    subparsers.add_parser("demo", help="Run the built-in sample validation demo")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "transcribe":
        cmd_transcribe(args.image_path)
    elif args.command == "transcribe-dir":
        cmd_transcribe_dir(args.image_dir, args.output_path)
    elif args.command == "transcribe-validate":
        cmd_transcribe_validate(args.image_dir, args.reference_file, args.output_path)
    elif args.command == "validate":
        cmd_validate_with_output(args.student_file, args.reference_file, args.output_path)
    elif args.command == "demo":
        cmd_demo()


if __name__ == "__main__":
    main()
