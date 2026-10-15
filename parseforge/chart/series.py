"""Chart data-series extraction.

A chart region is decoded into one or more ``DataSeries`` (name + numeric points).
The extraction is deterministic: given the chart key, we synthesize points whose
values are stable, so the structured JSON is reproducible and testable. In a real
parser this is the chart-to-table decoder output.
"""
from dataclasses import dataclass, field
from typing import List

from ..utils.hash import stable_float


@dataclass
class DataSeries:
    name: str
    points: List[float] = field(default_factory=list)

    def as_dict(self):
        return {"name": self.name, "points": [round(p, 3) for p in self.points]}


def extract_series(key, n_series, n_points, trend=0.0):
    """Return ``n_series`` synthetic series with a monotone-friendly trend.

    ``trend`` biases point values upward (used by the trainable mock so a higher
    skill yields cleaner series -- see ``parseforge.train``).
    """
    series = []
    for s in range(n_series):
        pts = []
        for p in range(n_points):
            base = stable_float("%s:%d:%d" % (key, s, p), 0.0, 10.0)
            pts.append(base + trend * p)
        series.append(DataSeries(name="series_%d" % (s + 1), points=pts))
    return series
