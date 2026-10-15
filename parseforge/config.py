"""Configuration dataclass + zero-dependency YAML loader.

When PyYAML is absent (the managed Python has no third-party deps), we fall back
to :mod:`parseforge.utils.yamlish`.
"""
from dataclasses import dataclass, field
from pathlib import Path

from .utils.yamlish import parse

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


@dataclass
class VisionConfig:
    patch_size: int = 8
    img_size: int = 32
    dim: int = 32
    depth: int = 2
    heads: int = 4


@dataclass
class AudioConfig:
    frame_size: int = 16
    n_frames: int = 8
    dim: int = 32


@dataclass
class LayoutConfig:
    min_area: int = 4
    score_threshold: float = 0.5


@dataclass
class TableConfig:
    max_rows: int = 12
    max_cols: int = 8


@dataclass
class ChartConfig:
    max_series: int = 6
    max_points: int = 12


@dataclass
class DecodeConfig:
    max_tokens: int = 128
    temperature: float = 0.7
    top_p: float = 0.9
    schema_mode: str = "auto"


@dataclass
class ModelConfig:
    name: str = "mock"
    dim: int = 32
    skill: float = 0.5


@dataclass
class ServingConfig:
    host: str = "127.0.0.1"
    port: int = 8000


@dataclass
class Config:
    vision: VisionConfig = field(default_factory=VisionConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    layout: LayoutConfig = field(default_factory=LayoutConfig)
    table: TableConfig = field(default_factory=TableConfig)
    chart: ChartConfig = field(default_factory=ChartConfig)
    decode: DecodeConfig = field(default_factory=DecodeConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    serving: ServingConfig = field(default_factory=ServingConfig)
    seed: int = 42

    @classmethod
    def from_dict(cls, d):
        def i(v, default):
            return int(v) if v is not None else default

        def f(v, default):
            return float(v) if v is not None else default

        def s(v, default):
            return str(v) if v is not None else default

        vision = d.get("vision", {}) or {}
        audio = d.get("audio", {}) or {}
        layout = d.get("layout", {}) or {}
        table = d.get("table", {}) or {}
        chart = d.get("chart", {}) or {}
        decode = d.get("decode", {}) or {}
        model = d.get("model", {}) or {}
        serving = d.get("serving", {}) or {}
        return cls(
            vision=VisionConfig(
                patch_size=i(vision.get("patch_size"), 8),
                img_size=i(vision.get("img_size"), 32),
                dim=i(vision.get("dim"), 32),
                depth=i(vision.get("depth"), 2),
                heads=i(vision.get("heads"), 4),
            ),
            audio=AudioConfig(
                frame_size=i(audio.get("frame_size"), 16),
                n_frames=i(audio.get("n_frames"), 8),
                dim=i(audio.get("dim"), 32),
            ),
            layout=LayoutConfig(
                min_area=i(layout.get("min_area"), 4),
                score_threshold=f(layout.get("score_threshold"), 0.5),
            ),
            table=TableConfig(
                max_rows=i(table.get("max_rows"), 12),
                max_cols=i(table.get("max_cols"), 8),
            ),
            chart=ChartConfig(
                max_series=i(chart.get("max_series"), 6),
                max_points=i(chart.get("max_points"), 12),
            ),
            decode=DecodeConfig(
                max_tokens=i(decode.get("max_tokens"), 128),
                temperature=f(decode.get("temperature"), 0.7),
                top_p=f(decode.get("top_p"), 0.9),
                schema_mode=s(decode.get("schema_mode"), "auto"),
            ),
            model=ModelConfig(
                name=s(model.get("name"), "mock"),
                dim=i(model.get("dim"), 32),
                skill=f(model.get("skill"), 0.5),
            ),
            serving=ServingConfig(
                host=s(serving.get("host"), "127.0.0.1"),
                port=i(serving.get("port"), 8000),
            ),
            seed=i(d.get("seed"), 42),
        )


def load_config(path=None):
    if path is None:
        return Config()
    p = Path(path)
    if not p.exists():
        return Config()
    text = p.read_text(encoding="utf-8")
    if yaml is not None:
        data = yaml.safe_load(text) or {}
    else:
        data = parse(text)
    return Config.from_dict(data)
