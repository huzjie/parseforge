"""Tiny vector math helpers (pure Python, no numpy)."""
import math


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def l2(a):
    return math.sqrt(sum(x * x for x in a))


def normalize(a):
    n = l2(a)
    if n == 0:
        return [0.0] * len(a)
    return [x / n for x in a]


def cosine(a, b):
    na, nb = l2(a), l2(b)
    if na == 0 or nb == 0:
        return 0.0
    return dot(a, b) / (na * nb)
