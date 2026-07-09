from __future__ import annotations

import subprocess
import sys
import unittest
import tempfile
from pathlib import Path

from src.donut_transcriber import TranscriptionResult
from src.pipeline import transcribe_and_validate_directory


class FakeTranscriber:
    def transcribe_image(self, image_path: Path) -> TranscriptionResult:
        latex_by_name = {
            "step1.png": r"x^2 + y^2 = z^2",
            "step2.png": r"x^2 + y^2 - z^2 = 0",
        }
        return TranscriptionResult(latex=latex_by_name[image_path.name], source="fake")


class PipelineTests(unittest.TestCase):
    def test_demo_command_runs(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        pipeline_path = project_root / "src" / "pipeline.py"

        completed = subprocess.run(
            [sys.executable, str(pipeline_path), "demo"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        self.assertIn("is_valid", completed.stdout)

    def test_validate_command_writes_output_file(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        pipeline_path = project_root / "src" / "pipeline.py"

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            student_file = temp_path / "student.txt"
            reference_file = temp_path / "reference.txt"
            output_file = temp_path / "validation.json"

            student_file.write_text("x^2 + y^2 = z^2\n", encoding="utf-8")
            reference_file.write_text("x^2 + y^2 - z^2 = 0\n", encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(pipeline_path),
                    "validate",
                    str(student_file),
                    str(reference_file),
                    "--output",
                    str(output_file),
                ],
                cwd=project_root,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, msg=completed.stderr)
            self.assertTrue(output_file.exists())
            self.assertIn("is_valid", output_file.read_text(encoding="utf-8"))

    def test_transcribe_and_validate_directory_wires_both_steps(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            image_dir = temp_path / "images"
            image_dir.mkdir()
            (image_dir / "step1.png").write_bytes(b"fake")
            (image_dir / "step2.png").write_bytes(b"fake")

            reference_file = temp_path / "reference.txt"
            reference_file.write_text("x^2 + y^2 = z^2\nx^2 + y^2 - z^2 = 0\n", encoding="utf-8")

            payload = transcribe_and_validate_directory(image_dir, reference_file, FakeTranscriber())

            self.assertEqual(len(payload["transcriptions"]), 2)
            self.assertEqual(len(payload["validation_results"]), 2)
            self.assertTrue(payload["validation_results"][0]["is_valid"])
            self.assertTrue(payload["validation_results"][1]["is_valid"])


if __name__ == "__main__":
    unittest.main()
