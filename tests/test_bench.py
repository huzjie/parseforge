import unittest

from parseforge.config import Config
from parseforge.bench.omnidocbench import OmniDocBench


class TestBench(unittest.TestCase):
    def test_evaluate(self):
        cfg = Config.from_dict({"model": {"name": "cpu"}})
        bench = OmniDocBench(cfg)
        scores = bench.evaluate(n_docs=4)
        self.assertAlmostEqual(scores["region_accuracy"], 1.0)
        self.assertAlmostEqual(scores["json_structure_f1"], 1.0)

    def test_train_demo(self):
        cfg = Config.from_dict({"model": {"name": "mock", "skill": 0.5}})
        bench = OmniDocBench(cfg)
        before = bench.evaluate(n_docs=3)
        for _ in range(20):
            bench.backend.train_step()
        after = bench.evaluate(n_docs=3)
        self.assertGreaterEqual(after["region_accuracy"], before["region_accuracy"])


if __name__ == "__main__":
    unittest.main()
