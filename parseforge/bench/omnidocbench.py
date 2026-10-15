"""OmniDocBench harness: synthesize docs, run backend, score."""
from ..config import load_config
from ..backends import get_backend
from ..oracle import synthesize_document
from .metrics import region_accuracy, cell_accuracy, series_mse, json_structure_f1


class OmniDocBench:
    def __init__(self, cfg):
        self.cfg = cfg
        self.backend = get_backend(cfg.model.name, cfg)

    def score_one(self, doc, result=None):
        if result is None:
            result = self.backend.parse(doc)
        return {
            "region_accuracy": region_accuracy(doc, result),
            "cell_accuracy": cell_accuracy(doc, result, self.cfg),
            "series_mse": series_mse(doc, result, self.cfg),
            "json_structure_f1": json_structure_f1(result),
        }

    def evaluate(self, n_docs=8, prefix="bench"):
        totals = {"region_accuracy": 0.0, "cell_accuracy": 0.0,
                  "series_mse": 0.0, "json_structure_f1": 0.0}
        for k in range(n_docs):
            doc = synthesize_document("%s-%d" % (prefix, k), n_regions=8)
            s = self.score_one(doc)
            for key in totals:
                totals[key] += s[key]
        return {key: v / n_docs for key, v in totals.items()}


def run_bench(config_path=None):
    cfg = load_config(config_path)
    bench = OmniDocBench(cfg)
    scores = bench.evaluate(n_docs=8)
    print("[bench] backend=%s skill=%.3f" % (bench.backend.name, bench.backend.skill))
    print("[bench] region_accuracy  = %.4f" % scores["region_accuracy"])
    print("[bench] cell_accuracy    = %.4f" % scores["cell_accuracy"])
    print("[bench] series_mse       = %.4f" % scores["series_mse"])
    print("[bench] json_structure_f1= %.4f" % scores["json_structure_f1"])
    return scores


def run_train_demo(config_path=None, steps=20, lr=0.025):
    cfg = load_config(config_path)
    bench = OmniDocBench(cfg)
    before = bench.evaluate(n_docs=6, prefix="train-before")
    skill0 = bench.backend.skill
    for _ in range(steps):
        bench.backend.train_step(lr=lr)
    skill1 = bench.backend.skill
    after = bench.evaluate(n_docs=6, prefix="train-after")
    print("[train] skill %.3f -> %.3f" % (skill0, skill1))
    print("[train] region_accuracy %.4f -> %.4f"
          % (before["region_accuracy"], after["region_accuracy"]))
    print("[train] cell_accuracy   %.4f -> %.4f"
          % (before["cell_accuracy"], after["cell_accuracy"]))
    print("[train] series_mse      %.4f -> %.4f"
          % (before["series_mse"], after["series_mse"]))
    return before, after
