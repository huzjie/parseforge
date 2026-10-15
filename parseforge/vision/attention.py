"""Multi-head self-attention (pure Python)."""
import math

from ..tensor import Tensor, matmul, softmax_rows


class MultiHeadAttention:
    """Scaled dot-product attention over ``dim`` with ``heads`` heads."""

    def __init__(self, dim, heads):
        assert dim % heads == 0, "dim must divide heads"
        self.dim = dim
        self.heads = heads
        self.head_dim = dim // heads
        # deterministic Q/K/V/O projections (dim x dim)
        self.wq = [[self._w(r, c, 1) for c in range(dim)] for r in range(dim)]
        self.wk = [[self._w(r, c, 2) for c in range(dim)] for r in range(dim)]
        self.wv = [[self._w(r, c, 3) for c in range(dim)] for r in range(dim)]
        self.wo = [[self._w(r, c, 4) for c in range(dim)] for r in range(dim)]

    @staticmethod
    def _w(r, c, salt):
        return math.sin((r + 1) * (c + 1) * 0.19 + salt) * 0.1

    def __call__(self, x):
        q = matmul(x, Tensor(self.wq))
        k = matmul(x, Tensor(self.wk))
        v = matmul(x, Tensor(self.wv))
        # split heads, attend, merge
        out = []
        hd = self.head_dim
        for h in range(self.heads):
            qh = [row[h * hd:(h + 1) * hd] for row in q.data]
            kh = [row[h * hd:(h + 1) * hd] for row in k.data]
            vh = [row[h * hd:(h + 1) * hd] for row in v.data]
            scores = []
            for qr in qh:
                row_scores = []
                for kr in kh:
                    s = sum(a * b for a, b in zip(qr, kr)) / math.sqrt(hd)
                    row_scores.append(s)
                scores.append(row_scores)
            attn = softmax_rows(Tensor(scores))
            head_out = matmul(attn, Tensor(vh))
            out.append(head_out.data)
        # concat heads -> dim
        merged = []
        for i in range(len(x.data)):
            merged.append(sum((out[h][i] for h in range(self.heads)), []))
        return matmul(Tensor(merged), Tensor(self.wo))
