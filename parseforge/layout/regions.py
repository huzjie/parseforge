"""Region detection: assign a semantic type to each detected box.

In a real parser this is a detection + classification head. Here we model the
decision with a deterministic score per candidate type, so the detector is
reproducible and testable. The type vocabulary matches Youtu-Parsing-Omni's
output taxonomy: title / text / table / chart / formula / figure.
"""
from .bbox import BBox

TYPES = ["title", "text", "table", "chart", "formula", "figure"]

# geometric priors: (min_ratio, max_ratio, kind) -- kind drives the score
_PRIORS = {
    "title":  (3.0, 20.0),
    "text":   (1.0, 20.0),
    "table":  (0.5, 4.0),
    "chart":  (0.5, 4.0),
    "formula":(1.0, 8.0),
    "figure": (0.5, 4.0),
}


class RegionDetector:
    """Detect typed regions from raw candidate boxes.

    Each candidate is ``{"bbox": [x0,y0,x1,y1], "score": float}``. The detector
    scores every type against the box geometry and picks the argmax. This is the
    "layout head" reduced to its essential, testable core.
    """

    def __init__(self, min_area=4, threshold=0.5):
        self.min_area = min_area
        self.threshold = threshold

    def _type_score(self, box, typ):
        w = max(1, box.x1 - box.x0)
        h = max(1, box.y1 - box.y0)
        ratio = w / h
        lo, hi = _PRIORS[typ]
        if ratio < lo or ratio > hi:
            return 0.0
        # within-range -> a baseline score plus a small deterministic tie-break
        return 0.6 + 0.4 * ((ratio - lo) / max(1e-6, (hi - lo)))

    def detect(self, candidates):
        regions = []
        for cand in candidates:
            x0, y0, x1, y1 = cand["bbox"]
            box = BBox(x0, y0, x1, y1)
            if box.area < self.min_area:
                continue
            scored = [(self._type_score(box, t), t) for t in TYPES]
            scored.sort(reverse=True)
            best_score, best_type = scored[0]
            if best_score < self.threshold:
                best_type = "text"
            regions.append({
                "type": best_type,
                "bbox": box.as_dict(),
                "score": round(best_score, 4),
            })
        return regions
