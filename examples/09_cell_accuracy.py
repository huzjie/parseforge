import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from parseforge.config import Config
from parseforge.engine import OmniParser
from parseforge.oracle import synthesize_document
from parseforge.bench.metrics import cell_accuracy

for skill in (0.5, 0.7, 1.0):
    cfg = Config.from_dict({"model": {"name": "mock", "skill": skill}})
    parser = OmniParser(cfg)
    doc = synthesize_document("cells-%.1f" % skill, n_regions=12)
    acc = cell_accuracy(doc, parser.parse(doc), cfg)
    print("skill=%.1f -> cell_accuracy=%.4f" % (skill, acc))
