import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
"""Run layout + table + chart recognition pieces directly."""
from parseforge.layout.regions import RegionDetector
from parseforge.layout.reading_order import reading_order
from parseforge.table.cells import cells_to_rows
from parseforge.chart.series import extract_series

det = RegionDetector(min_area=1, threshold=0.5)
cands = [{"bbox": [0, 0, 40, 10], "score": 0.9},
         {"bbox": [0, 20, 20, 20], "score": 0.9}]
regions = det.detect(cands)
print("regions:", regions)
print("order:", reading_order(regions))
print("cells:", cells_to_rows("t", 3, 2))
print("series:", [s.as_dict() for s in extract_series("c", 2, 5)])
