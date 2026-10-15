"""Chart legend reading: map color/line keys to series names."""
from dataclasses import dataclass
from typing import List


@dataclass
class Legend:
    entries: List[str]

    def as_dict(self):
        return {"entries": self.entries}


def read_legend(n_series):
    """Deterministic legend for ``n_series`` (series_1 .. series_n)."""
    return Legend(entries=["series_%d" % (i + 1) for i in range(n_series)])
