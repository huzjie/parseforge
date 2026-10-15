import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from parseforge.layout.reading_order import reading_order

regions = [
    {"bbox": {"x0": 0, "y0": 80, "x1": 40, "y1": 100}},
    {"bbox": {"x0": 0, "y0": 0, "x1": 40, "y1": 20}},
    {"bbox": {"x0": 0, "y0": 40, "x1": 40, "y1": 60}},
]
print("reading order:", reading_order(regions))
