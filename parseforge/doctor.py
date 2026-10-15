"""Self-check: instantiate every backend and parse a synthetic document."""
from .config import load_config
from .oracle import synthesize_document
from .backends import list_backends, get_backend


def run_doctor(config_path=None):
    cfg = load_config(config_path)
    doc = synthesize_document("doctor-0", n_regions=8)
    print("[doctor] config model=%s dim=%d" % (cfg.model.name, cfg.model.dim))
    results = []
    for name in list_backends():
        b = get_backend(name, cfg)
        res = b.parse(doc)
        n_blocks = len(res.blocks)
        results.append((name, n_blocks, res.schema_valid))
        print("[doctor] backend=%-14s blocks=%d schema_valid=%s mode=%s"
              % (name, n_blocks, res.schema_valid, getattr(b, "mode", "local")))
    print("[doctor] OK %d backends" % len(results))
    return results


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=None)
    args = ap.parse_args()
    run_doctor(args.config)
