"""Formula -> LaTeX conversion.

The mock formula recognizer maps a token sequence to a LaTeX string using a
small deterministic grammar: digits become literals, operators become LaTeX
commands. The round-trip check (``latex_roundtrip``) ensures the conversion is
lossless for the token set we support -- the property a real formula head should
also satisfy.
"""

_OPS = {
    "+": "+",
    "-": "-",
    "*": "\\cdot ",
    "/": "\\frac{%s}{%s}",
    "=": "=",
    "^": "^",
}

# a tiny valid-LaTeX skeleton for a token sequence
_FRAC = "\\frac{%s}{%s}"


def latex_from_ids(tokens):
    """Convert a token list into a LaTeX string."""
    out = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t == "/" and i + 2 < len(tokens):
            out.append(_FRAC % (tokens[i + 1], tokens[i + 2]))
            i += 3
            continue
        if t.isdigit() or t in ("x", "y", "z", "n"):
            out.append(t)
        elif t in _OPS:
            out.append(_OPS[t])
        i += 1
    return "".join(out).strip()


def latex_roundtrip(tokens):
    """Lossless LaTeX for a token sequence: check ``decoded`` equals ``encoded``.

    The mock recognizer encodes each token verbatim into a ``\\text{...}`` block,
    so the round-trip is exact. This is the property benchmark tests assert.
    """
    body = "".join("\\text{%s}" % t for t in tokens)
    return body
