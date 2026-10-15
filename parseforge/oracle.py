"""Deterministic oracle: the single source of truth for synthetic documents.

Both the mock backend and the OmniDocBench harness derive ground truth from these
functions, so a backend with ``skill=1.0`` matches the oracle *exactly* and scores
1.0, while ``skill=0.5`` sits at a random baseline. This is the same "shared seed
reproduction" trick that keeps the trainable mock monotone and testable.
"""
from .utils.hash import stable_float, stable_ints

TYPES = ["title", "text", "table", "chart", "formula", "figure"]


def oracle_region_type(doc_id, idx):
    """Deterministic gold type for region ``idx`` of ``doc_id``."""
    return TYPES[stable_ints("oracle:type:%s:%d" % (doc_id, idx), 1, 0, len(TYPES))[0]]


def oracle_text(doc_id, idx):
    """Deterministic gold text for a title/text region."""
    return "section %s content of %s" % (idx, doc_id)


def oracle_cell(doc_id, region_idx, i, j):
    """Deterministic gold cell value for a table region."""
    return round(stable_float("oracle:cell:%s:%d:%d:%d" % (doc_id, region_idx, i, j), 1, 999), 2)


def oracle_series_point(doc_id, region_idx, s, p):
    """Deterministic gold data point for a chart region."""
    return stable_float("oracle:series:%s:%d:%d:%d" % (doc_id, region_idx, s, p), 0.0, 10.0)


def synthesize_document(doc_id, n_regions=8):
    """Build a synthetic Document: text + layout candidates with gold types."""
    from .parse import Document
    candidates = []
    for i in range(n_regions):
        y0 = i * 40
        w = stable_ints("syn:w:%s:%d" % (doc_id, i), 1, 120, 360)[0]
        h = stable_ints("syn:h:%s:%d" % (doc_id, i), 1, 18, 44)[0]
        candidates.append({
            "bbox": [0, y0, w, y0 + h],
            "score": round(stable_float("syn:score:%s:%d" % (doc_id, i), 0.5, 1.0), 4),
        })
    return Document(doc_id=doc_id, text="document %s" % doc_id,
                    candidates=candidates)
