"""Table structure: a grid model of rows/cols with optional header."""
from dataclasses import dataclass, field
from typing import List


@dataclass
class TableStructure:
    n_rows: int
    n_cols: int
    has_header: bool = True
    # cells[i][j] -> text content (may be None for empty)
    cells: List[List] = field(default_factory=list)

    def as_dict(self):
        rows = []
        for i in range(self.n_rows):
            row = []
            for j in range(self.n_cols):
                row.append(self.cells[i][j] if i < len(self.cells) and j < len(self.cells[i]) else None)
            rows.append(row)
        return {
            "type": "table",
            "n_rows": self.n_rows,
            "n_cols": self.n_cols,
            "has_header": self.has_header,
            "rows": rows,
        }
