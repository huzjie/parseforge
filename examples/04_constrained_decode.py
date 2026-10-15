import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
"""Demonstrate the constrained JSON decoder's finite-state validation."""
from parseforge.decode.constrained import ConstrainedDecoder

cd = ConstrainedDecoder()
for token in '{"doc_id": "x", "blocks": []}':
    assert cd.legal(token), "illegal token %r" % token
print("complete=%s" % cd.is_complete())

bad = ConstrainedDecoder()
for token in '{"a":}':
    print("token %r legal=%s" % (token, bad.legal(token)))
