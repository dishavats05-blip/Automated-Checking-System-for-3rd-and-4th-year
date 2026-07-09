from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class InternFConfig:
    project_root: Path = Path(__file__).resolve().parents[1]
    data_dir: Path = project_root / "data"
    outputs_dir: Path = project_root / "outputs"
    donut_model_name: str = "HamAndCheese82/math-ocr-donut-v2"


CONFIG = InternFConfig()
