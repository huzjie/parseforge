import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
"""Run every backend and print block counts."""
from parseforge.config import Config
from parseforge.backends import list_backends, get_backend
from parseforge.oracle import synthesize_document

doc = synthesize_document("demo-2", n_regions=8)
for name in list_backends():
    backend = get_backend(name, Config())
    result = backend.parse(doc)
    print("%-14s -> %d blocks, schema_valid=%s"
          % (name, len(result.blocks), result.schema_valid))
