import unittest

from parseforge.config import Config
from parseforge.engine import OmniParser
from parseforge.oracle import synthesize_document
from parseforge.backends import list_backends
from parseforge.bench.metrics import region_accuracy, cell_accuracy


class TestEngine(unittest.TestCase):
    def test_all_backends_parse(self):
        for name in list_backends():
            cfg = Config.from_dict({"model": {"name": name}})
            parser = OmniParser(cfg)
            doc = synthesize_document("t-%s" % name, n_regions=6)
            result = parser.parse(doc)
            self.assertTrue(result.schema_valid, name)
            self.assertGreater(len(result.blocks), 0)

    def test_cpu_perfect(self):
        cfg = Config.from_dict({"model": {"name": "cpu"}})
        parser = OmniParser(cfg)
        doc = synthesize_document("perfect", n_regions=8)
        result = parser.parse(doc)
        self.assertAlmostEqual(region_accuracy(doc, result), 1.0)

    def test_mock_trainable(self):
        cfg = Config.from_dict({"model": {"name": "mock", "skill": 0.5}})
        parser = OmniParser(cfg)
        doc = synthesize_document("train", n_regions=8)
        r0 = region_accuracy(doc, parser.parse(doc))
        for _ in range(40):
            parser.train_step()
        r1 = region_accuracy(doc, parser.parse(doc))
        self.assertGreaterEqual(r1, r0)


if __name__ == "__main__":
    unittest.main()
