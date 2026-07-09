from __future__ import annotations

import importlib
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List

from PIL import Image

from .config import CONFIG

logger = logging.getLogger(__name__)


@dataclass
class TranscriptionResult:
    latex: str
    source: str


class DonutMathTranscriber:
    def __init__(self, model_name: str = CONFIG.donut_model_name) -> None:
        self.model_name = model_name
        self._processor = None
        self._model = None

    def _lazy_load(self) -> None:
        if self._processor is not None and self._model is not None:
            return

        try:
            transformers_module = importlib.import_module("transformers")
            DonutProcessor = transformers_module.DonutProcessor
            VisionEncoderDecoderModel = transformers_module.VisionEncoderDecoderModel
        except Exception as exc:
            logger.exception("transformers is unavailable for Donut transcription")
            raise RuntimeError("transformers is required for Donut transcription") from exc

        try:
            self._processor = DonutProcessor.from_pretrained(self.model_name)
            self._model = VisionEncoderDecoderModel.from_pretrained(self.model_name)
            self._model.eval()
        except Exception as exc:
            self._processor = None
            self._model = None
            logger.exception("Failed to load Donut model '%s'", self.model_name)
            raise RuntimeError(f"Failed to load Donut model '{self.model_name}'") from exc

    def transcribe_image(self, image_path: str | Path) -> TranscriptionResult:
        image = Image.open(image_path).convert("RGB")

        self._lazy_load()

        try:
            importlib.import_module("torch")

            pixel_values = self._processor(image, return_tensors="pt").pixel_values
            generated_ids = self._model.generate(pixel_values)
            latex = self._processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            latex = latex.strip()
            if not latex:
                raise RuntimeError("Donut model returned an empty transcription")
            return TranscriptionResult(latex=latex, source="donut")
        except Exception as exc:
            logger.exception("Donut inference failed for '%s'", image_path)
            raise RuntimeError(f"Donut inference failed for '{image_path}'") from exc


def transcribe_math_image(image_path: str | Path) -> TranscriptionResult:
    return DonutMathTranscriber().transcribe_image(image_path)


def transcribe_math_directory(image_dir: str | Path) -> List[TranscriptionResult]:
    directory = Path(image_dir)
    transcriber = DonutMathTranscriber()
    results: List[TranscriptionResult] = []

    for image_path in sorted(directory.iterdir()):
        if image_path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            continue
        results.append(transcriber.transcribe_image(image_path))

    return results
