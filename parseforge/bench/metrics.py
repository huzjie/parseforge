"""Metrics for structured document parsing quality.

The four metrics map directly to Youtu-Parsing-Omni's OmniDocBench evaluation:

* ``region_accuracy``  -- did the layout head label each region correctly?
* ``cell_accuracy``    -- did the table decoder read every cell correctly?
* ``series_mse``       -- did the chart decoder reproduce the data series?
* ``json_structure_f1``-- is the emitted JSON structurally well-formed?
"""
from ..oracle import oracle_region_type, oracle_cell, oracle_series_point


def _blocks_by_region(result):
    return {b.get("region_id", i): b for i, b in enumerate(result.blocks)}


def _table_dims(cfg):
    return min(cfg.table.max_rows, 4), min(cfg.table.max_cols, 3)


def _chart_dims(cfg):
    return min(cfg.chart.max_series, 2), min(cfg.chart.max_points, 5)


def region_accuracy(doc, result):
    by_region = _blocks_by_region(result)
    n = len(doc.candidates)
    if n == 0:
        return 1.0
    correct = 0
    for idx in range(n):
        gold = oracle_region_type(doc.doc_id, idx)
        pred = by_region[idx]["type"] if idx in by_region else "text"
        if pred == gold:
            correct += 1
    return correct / n


def cell_accuracy(doc, result, cfg):
    by_region = _blocks_by_region(result)
    n_rows, n_cols = _table_dims(cfg)
    total = correct = 0
    for idx in range(len(doc.candidates)):
        if oracle_region_type(doc.doc_id, idx) != "table":
            continue
        blk = by_region.get(idx)
        if blk is None or blk["type"] != "table":
            total += n_rows * n_cols
            continue
        rows = blk["content"]["rows"]
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                total += 1
                if val == oracle_cell(doc.doc_id, idx, i, j):
                    correct += 1
    return correct / total if total else 1.0


def series_mse(doc, result, cfg):
    by_region = _blocks_by_region(result)
    n_series, n_points = _chart_dims(cfg)
    se = 0.0
    npts = 0
    for idx in range(len(doc.candidates)):
        if oracle_region_type(doc.doc_id, idx) != "chart":
            continue
        blk = by_region.get(idx)
        if blk is None or blk["type"] != "chart":
            for s in range(n_series):
                for p in range(n_points):
                    g = oracle_series_point(doc.doc_id, idx, s, p)
                    se += (0.0 - g) ** 2
                    npts += 1
            continue
        series = blk["content"]["series"]
        for s, sr in enumerate(series):
            for p, val in enumerate(sr["points"]):
                g = oracle_series_point(doc.doc_id, idx, s, p)
                se += (val - g) ** 2
                npts += 1
    return se / npts if npts else 0.0


def json_structure_f1(result):
    """Reward structurally valid JSON: 1.0 if valid, 0.0 otherwise."""
    return 1.0 if result.schema_valid else 0.0
