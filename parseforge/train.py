"""Trainable mock: show the skill signal monotonically improving parse quality.

The mock backend's ``skill`` is the only trainable state. Each ``train_step``
increments it (delta always positive), and because every metric is a monotone
function of skill, OmniDocBench scores climb 0.5-baseline -> ~1.0.
"""
from .config import load_config
from .backends import get_backend
from .bench.metrics import region_accuracy, cell_accuracy, series_mse
from .oracle import synthesize_document


def train(config_path=None, steps=20, lr=0.025, every=5):
    cfg = load_config(config_path)
    backend = get_backend(cfg.model.name, cfg)
    doc = synthesize_document("train-demo", n_regions=8)
    rows = []
    for step in range(steps + 1):
        res = backend.parse(doc)
        row = {
            "step": step,
            "skill": round(backend.skill, 3),
            "region_acc": round(region_accuracy(doc, res), 4),
            "cell_acc": round(cell_accuracy(doc, res, cfg), 4),
            "series_mse": round(series_mse(doc, res, cfg), 4),
        }
        rows.append(row)
        if step < steps:
            backend.train_step(lr=lr)
    for r in rows:
        if r["step"] % every == 0 or r["step"] == steps:
            print("[train] step=%2d skill=%.3f region_acc=%.4f cell_acc=%.4f mse=%.4f"
                  % (r["step"], r["skill"], r["region_acc"], r["cell_acc"], r["series_mse"]))
    return rows


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=None)
    ap.add_argument("--steps", type=int, default=20)
    ap.add_argument("--lr", type=float, default=0.025)
    args = ap.parse_args()
    train(args.config, steps=args.steps, lr=args.lr)
