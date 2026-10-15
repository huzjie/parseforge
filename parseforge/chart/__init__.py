"""Chart understanding: turn a visual chart into structured data series."""
from .series import DataSeries, extract_series
from .legend import Legend, read_legend

__all__ = ["DataSeries", "extract_series", "Legend", "read_legend"]
