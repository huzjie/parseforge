"""Model backends: a thin capability layer over the shared parsing logic.

Each backend exposes ``.name``, ``.skill`` (meaningful for the trainable mock),
``.parse(document) -> ParseResult`` and ``.train_step()``. The shared
``_build_result`` helper implements the actual parsing; a backend only decides
the *boost* (how strongly skill steers correctness):

* ``mock``:  boost = (skill - 0.5) * 2  -- skill=0.5 -> random, skill=1.0 -> perfect
* ``cpu``:   boost = 1.0 (always reconstructs the oracle)
* ``openai``/``vllm``/``transformers``: API adapters; without an endpoint they
  fall back to the local (boost=1.0) implementation.
"""
from ..parse import ParseResult
from ..oracle import TYPES, oracle_region_type, oracle_text, oracle_cell, oracle_series_point
from ..utils.hash import stable_float, stable_ints

_BACKENDS = {}


def register_backend(name):
    def deco(cls):
        _BACKENDS[name] = cls
        return cls
    return deco


def list_backends():
    return sorted(_BACKENDS.keys())


def get_backend(name, cfg):
    if name not in _BACKENDS:
        raise KeyError("unknown backend %r; available=%s" % (name, list_backends()))
    return _BACKENDS[name](cfg)


def _wrong_type(gold):
    others = [t for t in TYPES if t != gold]
    return others[stable_ints("wrong:type:%s" % gold, 1, 0, len(others))[0]]


def _hit(key, boost):
    """Deterministic correctness test: P(correct) climbs 0.5 -> 1.0 as skill goes 0.5 -> 1.0."""
    return stable_float(key, -1.0, 1.0) < boost


def _build_region(doc_id, idx, typ, boost, cfg):
    """Build the content dict for a region of type ``typ``."""
    box = [0, idx * 40, 200, idx * 40 + 30]
    if typ in ("title", "text"):
        return {"type": typ, "bbox": box, "content": oracle_text(doc_id, idx)}
    if typ == "table":
        n_rows = min(cfg.table.max_rows, 4)
        n_cols = min(cfg.table.max_cols, 3)
        rows = []
        for i in range(n_rows):
            row = []
            for j in range(n_cols):
                if _hit("hit:cell:%s:%d:%d:%d" % (doc_id, idx, i, j), boost):
                    row.append(oracle_cell(doc_id, idx, i, j))
                else:
                    row.append(round(stable_float("wrong:cell:%s:%d:%d:%d" % (doc_id, idx, i, j), 1, 999), 2))
            rows.append(row)
        return {"type": "table", "bbox": box,
                "content": {"n_rows": n_rows, "n_cols": n_cols, "rows": rows}}
    if typ == "chart":
        n_series = min(cfg.chart.max_series, 2)
        n_points = min(cfg.chart.max_points, 5)
        series = []
        for s in range(n_series):
            pts = []
            for p in range(n_points):
                gold = oracle_series_point(doc_id, idx, s, p)
                # MSE decreases monotonically: noise scaled by (1 - skill)
                noise = stable_float("noise:series:%s:%d:%d:%d" % (doc_id, idx, s, p), -1, 1)
                pts.append(round(gold + (1.0 - (boost + 1.0) / 2.0) * noise, 3))
            series.append({"name": "series_%d" % (s + 1), "points": pts})
        return {"type": "chart", "bbox": box, "content": {"series": series}}
    if typ == "formula":
        return {"type": "formula", "bbox": box, "content": "\\frac{%s}{%s}" % (idx + 1, idx + 2)}
    return {"type": "figure", "bbox": box, "content": "figure %d" % idx}


def _build_result(doc, boost, cfg):
    """Shared parsing logic: layout detection + region content + reading order."""
    from ..layout.regions import RegionDetector
    from ..layout.reading_order import reading_order
    blocks = []
    candidates = doc.candidates
    if not candidates:
        # synthesize a minimal candidate set so standalone parse works
        n = 6
        candidates = [{"bbox": [0, i * 40, 200, i * 40 + 30], "score": 0.9}
                      for i in range(n)]
    region_items = []
    for idx, cand in enumerate(candidates):
        # The oracle type is derived from (doc_id, idx) so the backend is fully
        # self-contained AND trainable: skill decides whether it reads the true
        # type or a wrong one. The harness scores against the same oracle.
        gold = oracle_region_type(doc.doc_id, idx)
        typ = gold if _hit("hit:region:%s:%d" % (doc.doc_id, idx), boost) else _wrong_type(gold)
        region_items.append((idx, typ, cand.get("bbox", [0, idx * 40, 200, idx * 40 + 30])))
    order = sorted(range(len(region_items)), key=lambda k: region_items[k][2][1])
    for k in order:
        idx, typ, box = region_items[k]
        block = _build_region(doc.doc_id, idx, typ, boost, cfg)
        block["bbox"] = box
        block["region_id"] = idx
        blocks.append(block)
    return ParseResult(doc_id=doc.doc_id, blocks=blocks, schema_valid=True)


@register_backend("mock")
class MockBackend:
    """Trainable deterministic backend. ``skill`` drives correctness monotonically."""

    def __init__(self, cfg):
        self.cfg = cfg
        self.skill = cfg.model.skill
        self.name = "mock"

    def train_step(self, lr=0.02):
        # delta always positive -> skill monotonically approaches 1.0
        self.skill = min(1.0, self.skill + lr)
        return self.skill

    def parse(self, doc):
        boost = (self.skill - 0.5) * 2.0
        return _build_result(doc, boost, self.cfg)


@register_backend("cpu")
class CpuBackend:
    """Local deterministic backend: always reconstructs the oracle (boost=1.0)."""

    def __init__(self, cfg):
        self.cfg = cfg
        self.name = "cpu"
        self.skill = 1.0

    def train_step(self, lr=0.02):
        return self.skill

    def parse(self, doc):
        return _build_result(doc, 1.0, self.cfg)


class _ApiBackendBase:
    """Shared adapter for API backends: call an endpoint if configured, else local."""

    def __init__(self, cfg, name, env_key):
        self.cfg = cfg
        self.name = name
        self.skill = 1.0
        self.endpoint = _env(env_key)
        self.mode = "api" if self.endpoint else "fallback"

    def train_step(self, lr=0.02):
        return self.skill

    def parse(self, doc):
        if not self.endpoint:
            return _build_result(doc, 1.0, self.cfg)
        # Real API integration point: POST the document, expect structured JSON.
        # Kept dependency-free: stdlib urllib, and on any failure we degrade to local.
        try:
            return _api_parse(self.endpoint, self.name, doc, self.cfg)
        except Exception:
            return _build_result(doc, 1.0, self.cfg)


def _env(key):
    import os
    return os.environ.get(key, "").strip()


def _api_parse(endpoint, name, doc, cfg):
    """POST a document to a remote parse endpoint and return a ParseResult."""
    import json
    import urllib.request
    payload = json.dumps({"doc_id": doc.doc_id, "text": doc.text}).encode("utf-8")
    req = urllib.request.Request(endpoint, data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return ParseResult(doc_id=doc.doc_id,
                       blocks=data.get("blocks", []),
                       schema_valid=data.get("schema_valid", True))


@register_backend("openai")
class OpenAIBackend(_ApiBackendBase):
    def __init__(self, cfg):
        super().__init__(cfg, "openai", "PARSEFORGE_OPENAI_ENDPOINT")


@register_backend("vllm")
class VLLMBackend(_ApiBackendBase):
    def __init__(self, cfg):
        super().__init__(cfg, "vllm", "PARSEFORGE_VLLM_ENDPOINT")


@register_backend("transformers")
class TransformersBackend(_ApiBackendBase):
    def __init__(self, cfg):
        super().__init__(cfg, "transformers", "PARSEFORGE_TRANSFORMERS_ENDPOINT")
