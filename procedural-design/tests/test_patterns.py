# tests/test_patterns.py

import unittest
from src.utils.patterns import gray_scott_2d

class TestPatterns(unittest.TestCase):

    def test_gray_scott_2d_output_shape(self):
        nx, ny, steps, Du, Dv, F, K, rng_seed, n_seeds = 100, 100, 1000, 0.16, 0.08, 0.060, 0.062, 42, 6
        U, V = gray_scott_2d(nx, ny, steps, Du, Dv, F, K, rng_seed, n_seeds)
        self.assertEqual(U.shape, (ny, nx))
        self.assertEqual(V.shape, (ny, nx))

    def test_gray_scott_2d_values_range(self):
        nx, ny, steps, Du, Dv, F, K, rng_seed, n_seeds = 100, 100, 1000, 0.16, 0.08, 0.060, 0.062, 42, 6
        U, V = gray_scott_2d(nx, ny, steps, Du, Dv, F, K, rng_seed, n_seeds)
        self.assertTrue((U >= 0).all() and (U <= 1).all())
        self.assertTrue((V >= 0).all() and (V <= 1).all())

if __name__ == '__main__':
    unittest.main()