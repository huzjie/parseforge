"""Structured decoder: score a candidate output against an input summary.

The decoder head reduces "generate the structured JSON" to a scoring problem: it
embeds a candidate output string into the same space as the input summary and
scores their alignment. The mock backend uses this alignment score plus a skill
term to rank candidate JSON documents; the highest-scoring *valid* candidate is
returned. This mirrors contrastive decoding without needing a full LM.
"""
from ..utils.hash import stable_vector
from ..utils.vectors import dot, normalize


class StructuredDecoder:
    def __init__(self, dim):
        self.dim = dim

    def embed_candidate(self, cand_key):
        return stable_vector("cand:%s" % cand_key, self.dim, -0.2, 0.2)

    def score(self, summary, cand_key):
        cv = self.embed_candidate(cand_key)
        s = normalize(summary)
        c = normalize(cv)
        return dot(s, c)
