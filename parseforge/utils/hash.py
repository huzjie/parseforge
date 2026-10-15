"""Deterministic pseudo-random primitives.

Uses the first 8 bytes of md5(key) to seed a ``random.Random``. One md5 per key
is fast, high-entropy (no short-cycle repetition) and fully reproducible -- the
same key always yields the same value, which makes the mock backend and the
OmniDocBench harness deterministic.
"""
import hashlib
import random


def _rng(key):
    d = hashlib.md5(key.encode("utf-8")).digest()
    return random.Random(int.from_bytes(d[:8], "big"))


def stable_float(key, lo=0.0, hi=1.0):
    """A deterministic float in [lo, hi] derived from ``key``."""
    return _rng(key).uniform(lo, hi)


def stable_ints(key, n, lo=0, hi=100):
    """``n`` deterministic ints in [lo, hi) derived from ``key``."""
    r = _rng(key)
    return [r.randrange(lo, hi) for _ in range(n)]


def stable_bool(key, p=0.5):
    """A deterministic Bernoulli draw with probability ``p``."""
    return _rng(key).random() < p


def stable_vector(key, dim, lo=-1.0, hi=1.0):
    """A deterministic vector of length ``dim`` in [lo, hi]."""
    r = _rng(key)
    return [r.uniform(lo, hi) for _ in range(dim)]
