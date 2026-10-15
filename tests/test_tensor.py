import unittest

from parseforge.tensor import Tensor, matmul, softmax_rows, layernorm


class TestTensor(unittest.TestCase):
    def test_matmul_shape(self):
        a = Tensor([[1, 2], [3, 4]])
        b = Tensor([[5, 6], [7, 8]])
        c = matmul(a, b)
        self.assertEqual(c.shape, (2, 2))
        self.assertAlmostEqual(c.data[0][0], 19.0)

    def test_softmax_sums_to_one(self):
        x = Tensor([[1.0, 2.0, 3.0]])
        y = softmax_rows(x)
        self.assertAlmostEqual(sum(y.data[0]), 1.0, places=6)

    def test_layernorm_2d(self):
        x = Tensor([[1.0, 2.0, 3.0], [2.0, 4.0, 6.0]])
        y = layernorm(x)
        self.assertEqual(y.shape, (2, 3))


if __name__ == "__main__":
    unittest.main()
