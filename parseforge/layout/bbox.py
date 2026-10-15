"""Axis-aligned bounding boxes (integer coordinates)."""
from dataclasses import dataclass


@dataclass
class BBox:
    x0: int
    y0: int
    x1: int
    y1: int

    @property
    def area(self):
        return max(0, self.x1 - self.x0) * max(0, self.y1 - self.y0)

    @property
    def cy(self):
        return (self.y0 + self.y1) / 2.0

    @property
    def cx(self):
        return (self.x0 + self.x1) / 2.0

    def as_dict(self):
        return {"x0": self.x0, "y0": self.y0, "x1": self.x1, "y1": self.y1}


def iou(a, b):
    """Intersection over union of two boxes."""
    ix0 = max(a.x0, b.x0)
    iy0 = max(a.y0, b.y0)
    ix1 = min(a.x1, b.x1)
    iy1 = min(a.y1, b.y1)
    inter = max(0, ix1 - ix0) * max(0, iy1 - iy0)
    union = a.area + b.area - inter
    return inter / union if union > 0 else 0.0
