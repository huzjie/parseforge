"""Cell text extraction and row assembly."""
from ..utils.hash import stable_bool, stable_float


def cell_text(key, i, j):
    """Deterministic cell content for a synthetic table cell.

    In a real parser this is the OCR + language model read-out of the cell's
    crop. Here it produces stable tokens so downstream tests are reproducible.
    """
    if stable_bool("%s:empty:%d:%d" % (key, i, j), 0.12):
        return None
    base = round(stable_float("%s:val:%d:%d" % (key, i, j), 1, 999), 2)
    if i == 0:
        return "hdr_%d" % (j + 1)
    return "%s" % base


def cells_to_rows(key, n_rows, n_cols):
    """Build a full cell matrix ``n_rows x n_cols``."""
    rows = []
    for i in range(n_rows):
        rows.append([cell_text(key, i, j) for j in range(n_cols)])
    return rows
