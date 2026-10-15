"""Minimal text utilities (no external tokenizers)."""


def tokenize_ascii(text, vocab_size=4096):
    """One token per ascii word/punct; non-ascii kept as single tokens.

    Deterministic and lossless: the mock encoder uses this so token counts are
    real (length-scaled) rather than hand-waved.
    """
    tokens = []
    buf = []
    for ch in text:
        o = ord(ch)
        if ch.isalnum() and o < 128:
            buf.append(ch)
        else:
            if buf:
                tokens.append("".join(buf))
                buf = []
            tokens.append(ch)
    if buf:
        tokens.append("".join(buf))
    return tokens


def word_counts(text):
    return max(1, len(text.split()))
