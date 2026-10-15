"""Small zero-dependency utilities shared across parseforge."""
from .hash import stable_float, stable_ints, stable_bool, stable_vector
from .vectors import normalize, dot, cosine, l2
from .text import tokenize_ascii, word_counts

__all__ = [
    "stable_float",
    "stable_ints",
    "stable_bool",
    "stable_vector",
    "normalize",
    "dot",
    "cosine",
    "l2",
    "tokenize_ascii",
    "word_counts",
]
