"""A minimal pure-Python tensor for reference implementations.

Only the operations the model actually needs: add, sub, mul (broadcast), matmul
(via dot products), softmax, layer-norm. No numpy, no autograd -- clarity over
speed.
"""
import math


class Tensor:
    __slots__ = ("data", "shape")

    def __init__(self, data, shape=None):
        if not isinstance(data, list):
            data = [data]
        # normalize a flat list into a 2D row tensor
        if data and not isinstance(data[0], (list, tuple)):
            data = [list(data)]
        self.data = [[float(x) for x in row] for row in data]
        rows = len(self.data)
        cols = len(self.data[0]) if rows else 0
        for row in self.data:
            if len(row) != cols:
                raise ValueError("ragged tensor")
        self.shape = (rows, cols)

    @classmethod
    def zeros(cls, rows, cols):
        return cls([[0.0] * cols for _ in range(rows)])

    @classmethod
    def ones(cls, rows, cols):
        return cls([[1.0] * cols for _ in range(rows)])

    def __add__(self, other):
        if isinstance(other, Tensor):
            return Tensor([[a + b for a, b in zip(r, o)] for r, o in zip(self.data, other.data)])
        return Tensor([[a + other for a in r] for r in self.data])

    def __sub__(self, other):
        if isinstance(other, Tensor):
            return Tensor([[a - b for a, b in zip(r, o)] for r, o in zip(self.data, other.data)])
        return Tensor([[a - other for a in r] for r in self.data])

    def __mul__(self, other):
        if isinstance(other, Tensor):
            return Tensor([[a * b for a, b in zip(r, o)] for r, o in zip(self.data, other.data)])
        return Tensor([[a * other for a in r] for r in self.data])

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        return Tensor([[a / other for a in r] for r in self.data])

    def __getitem__(self, idx):
        return self.data[idx]

    def __repr__(self):
        return "Tensor(shape=%r)" % (self.shape,)


def dot_row(a, b):
    return sum(x * y for x, y in zip(a, b))


def matmul(a, b):
    """Matrix multiply (a: R x K, b: K x C) -> R x C."""
    if a.shape[1] != b.shape[0]:
        raise ValueError("matmul shape mismatch %r x %r" % (a.shape, b.shape))
    bt = list(zip(*b.data))
    return Tensor([[dot_row(row, col) for col in bt] for row in a.data])


def softmax_rows(x):
    out = []
    for row in x.data:
        m = max(row)
        exps = [math.exp(v - m) for v in row]
        s = sum(exps)
        out.append([e / s for e in exps])
    return Tensor(out)


def layernorm(x, eps=1e-5):
    out = []
    for row in x.data:
        mean = sum(row) / len(row)
        var = sum((v - mean) ** 2 for v in row) / len(row)
        inv = 1.0 / math.sqrt(var + eps)
        out.append([(v - mean) * inv for v in row])
    return Tensor(out)
