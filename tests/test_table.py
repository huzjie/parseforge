import unittest

from parseforge.table.structure import TableStructure
from parseforge.table.cells import cells_to_rows
from parseforge.table.span import detect_spans


class TestTable(unittest.TestCase):
    def test_cells_shape(self):
        rows = cells_to_rows("t", 4, 3)
        self.assertEqual(len(rows), 4)
        self.assertEqual(len(rows[0]), 3)

    def test_detect_spans(self):
        cells = [["a", "a", "b"], ["c", "d", "d"]]
        spans = detect_spans(cells)
        self.assertTrue(any(s["colspan"] == 2 for s in spans))

    def test_as_dict(self):
        ts = TableStructure(n_rows=2, n_cols=2, cells=[["a", "b"], ["c", "d"]])
        d = ts.as_dict()
        self.assertEqual(d["n_rows"], 2)


if __name__ == "__main__":
    unittest.main()
