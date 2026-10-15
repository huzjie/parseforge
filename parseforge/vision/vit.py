"""Vision tower: patch embedding -> attention blocks -> CLS + patch tokens."""
from ..tensor import layernorm
from .patch import PatchEmbedding
from .attention import MultiHeadAttention


class VisionTower:
    """A tiny ViT: ``depth`` blocks of attention + layer-norm.

    Returns the CLS token (the pooled image representation). The CLS token is
    implemented as the mean of all patch tokens after the final layer-norm, which
    is a reasonable pooling for document regions of fixed size.
    """

    def __init__(self, img_size, patch_size, dim, depth, heads):
        self.embed = PatchEmbedding(img_size, patch_size, dim)
        self.blocks = [MultiHeadAttention(dim, heads) for _ in range(depth)]
        self.dim = dim
        self.depth = depth

    def encode(self, image):
        x = self.embed(image)
        for block in self.blocks:
            h = block(x)
            x = layernorm(x + h)
        return x

    def cls(self, image):
        x = self.encode(image)
        n = len(x.data)
        return [sum(x.data[i][c] for i in range(n)) / n for c in range(self.dim)]
