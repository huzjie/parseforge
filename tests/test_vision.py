import unittest

from parseforge.vision.patch import PatchEmbedding
from parseforge.vision.vit import VisionTower
from parseforge.utils.hash import stable_vector


def _img(size=16):
    return [[0.5 for _ in range(size)] for _ in range(size)]


class TestVision(unittest.TestCase):
    def test_patch_embedding(self):
        pe = PatchEmbedding(img_size=16, patch_size=8, dim=32)
        out = pe(_img())
        self.assertEqual(out.shape, (4, 32))

    def test_vision_tower_cls(self):
        vt = VisionTower(img_size=16, patch_size=8, dim=16, depth=1, heads=2)
        cls = vt.cls(_img())
        self.assertEqual(len(cls), 16)


if __name__ == "__main__":
    unittest.main()
