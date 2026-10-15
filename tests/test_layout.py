import unittest

from parseforge.layout.bbox import BBox, iou
from parseforge.layout.regions import RegionDetector
from parseforge.layout.reading_order import reading_order


class TestLayout(unittest.TestCase):
    def test_iou(self):
        a = BBox(0, 0, 10, 10)
        b = BBox(5, 5, 15, 15)
        self.assertAlmostEqual(iou(a, b), 25 / 175, places=6)

    def test_region_detector(self):
        det = RegionDetector(min_area=1, threshold=0.5)
        cands = [{"bbox": [0, 0, 40, 10], "score": 0.9},
                 {"bbox": [0, 20, 10, 30], "score": 0.9}]
        regions = det.detect(cands)
        self.assertEqual(len(regions), 2)
        valid = ["title", "text", "table", "chart", "formula", "figure"]
        self.assertIn(regions[0]["type"], valid)
        self.assertIn(regions[1]["type"], valid)

    def test_reading_order(self):
        regions = [
            {"bbox": {"x0": 0, "y0": 20, "x1": 10, "y1": 30}},
            {"bbox": {"x0": 0, "y0": 0, "x1": 10, "y1": 10}},
        ]
        order = reading_order(regions)
        self.assertEqual(order, [1, 0])


if __name__ == "__main__":
    unittest.main()
