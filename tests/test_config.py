import unittest

from parseforge.config import Config, load_config
from parseforge.utils.yamlish import parse


class TestConfig(unittest.TestCase):
    def test_defaults(self):
        cfg = Config()
        self.assertEqual(cfg.model.name, "mock")
        self.assertEqual(cfg.vision.dim, 32)

    def test_from_dict(self):
        cfg = Config.from_dict({"model": {"name": "cpu", "skill": 0.9}})
        self.assertEqual(cfg.model.name, "cpu")
        self.assertAlmostEqual(cfg.model.skill, 0.9)

    def test_yamlish_block_list(self):
        data = parse("items:\n  - a\n  - b\n")
        self.assertEqual(data["items"], ["a", "b"])

    def test_yamlish_inline_comment(self):
        data = parse("name: mock  # note\n")
        self.assertEqual(data["name"], "mock")


if __name__ == "__main__":
    unittest.main()
