"""Patch embedding: split an image into patches and project to dim."""
import math

from ..tensor import Tensor


class PatchEmbedding:
    """Flatten ``patch_size x patch_size`` tiles into embedding vectors.

    The image is a list of ``img_size`` rows of ``img_size`` pixels. Each pixel
    value is a float in [0, 1]. Patches are row-major.
    """

    def __init__(self, img_size, patch_size, dim):
        assert img_size % patch_size == 0, "img_size must divide patch_size"
        self.img_size = img_size
        self.patch_size = patch_size
        self.dim = dim
        self.n_patches = (img_size // patch_size) ** 2
        # deterministic projection matrix (n_pixels x dim)
        self.proj = [[self._w(r, c) for c in range(dim)]
                     for r in range(patch_size * patch_size)]

    @staticmethod
    def _w(r, c):
        # deterministic pseudo-weight, stable across runs
        return math.sin((r + 1) * (c + 1) * 0.37) * 0.1

    def __call__(self, image):
        ps = self.patch_size
        patches = []
        for y in range(0, self.img_size, ps):
            for x in range(0, self.img_size, ps):
                flat = []
                for dy in range(ps):
                    for dx in range(ps):
                        flat.append(image[y + dy][x + dx])
                patches.append(flat)
        # project each patch: (n_patches x n_pixels) @ (n_pixels x dim)
        out = []
        for patch in patches:
            out.append([sum(p * self.proj[r][c] for r, p in enumerate(patch))
                        for c in range(self.dim)])
        return Tensor(out)
