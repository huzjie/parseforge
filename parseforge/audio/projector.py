"""Project audio frames into the shared embedding space."""
import math

from ..tensor import Tensor


class AudioProjector:
    """Maps ``frame_size``-dim frames to ``dim``, then pools across time.

    This is the audio counterpart of the vision patch embedding: both produce
    ``dim``-dimensional tokens so one decoder can consume either.
    """

    def __init__(self, frame_size, dim):
        self.frame_size = frame_size
        self.dim = dim
        self.proj = [[math.sin((r + 1) * (c + 1) * 0.23) * 0.1
                      for c in range(dim)] for r in range(frame_size)]

    def __call__(self, frames):
        """frames: n_frames x frame_size -> n_frames x dim (then mean-pool)."""
        out = []
        for frame in frames:
            out.append([sum(frame[r] * self.proj[r][c] for r in range(self.frame_size))
                        for c in range(self.dim)])
        n = len(out)
        return [sum(out[i][c] for i in range(n)) / n for c in range(self.dim)]
