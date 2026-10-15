"""Merged-cell (rowspan/colspan) detection.

Header cells that repeat the same value horizontally are a cheap, deterministic
signal for a ``colspan``; vertical repeats signal ``rowspan``. This is the
essence of span detection without a segmentation model.
"""


def detect_spans(cells):
    """Return a list of ``{i, j, colspan, rowspan}`` for merged cells."""
    if not cells:
        return []
    spans = []
    n_rows = len(cells)
    n_cols = len(cells[0])
    for i in range(n_rows):
        j = 0
        while j < n_cols:
            v = cells[i][j]
            if v is None:
                j += 1
                continue
            colspan = 1
            while j + colspan < n_cols and cells[i][j + colspan] == v:
                colspan += 1
            rowspan = 1
            while i + rowspan < n_rows and cells[i + rowspan][j] == v:
                rowspan += 1
            if colspan > 1 or rowspan > 1:
                spans.append({"i": i, "j": j, "colspan": colspan, "rowspan": rowspan})
            j += colspan
    return spans
