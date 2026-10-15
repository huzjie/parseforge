import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
"""Train the mock backend and watch scores climb."""
from parseforge.config import Config
from parseforge.engine import OmniParser
from parseforge.oracle import synthesize_document
from parseforge.bench.metrics import region_accuracy

parser = OmniParser(Config.from_dict({"model": {"name": "mock", "skill": 0.5}}))
doc = synthesize_document("demo-3", n_regions=8)

r0 = region_accuracy(doc, parser.parse(doc))
for _ in range(40):
    parser.train_step()
r1 = region_accuracy(doc, parser.parse(doc))
print("region_accuracy %.4f -> %.4f  (skill=%.2f)"
      % (r0, r1, parser.skill))
