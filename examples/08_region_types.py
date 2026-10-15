import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from parseforge.oracle import synthesize_document, oracle_region_type

doc = synthesize_document("types", n_regions=10)
for i, c in enumerate(doc.candidates):
    print("region %d -> %s  bbox=%s" % (i, oracle_region_type(doc.doc_id, i), c["bbox"]))
