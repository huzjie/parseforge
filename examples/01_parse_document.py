import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
"""Parse a synthetic document and print structured JSON."""
from parseforge.config import Config
from parseforge.engine import OmniParser
from parseforge.oracle import synthesize_document

parser = OmniParser(Config())
doc = synthesize_document("demo-1", n_regions=8)
result = parser.parse(doc)
print(result.to_json())
