__author__ = 'Federico Tomassetti'

import unittest
from lands.basic_map_operations import *


class TestBasicMapOperations(unittest.TestCase):

    def setUp(self):
        pass

    def test_random_point(self):
        for seed in [0, 1, 27, 29, 1939, 1982, 2015]:
            random.seed(seed)
            for n in range(10):
                x, y = random_point(100, 200)
                self.assertTrue(x >= 0,  "x is within boundaries")
                self.assertTrue(x < 100, "x is within boundaries")
                self.assertTrue(y >= 0,  "y is within boundaries")
                self.assertTrue(y < 200, "y is within boundaries")

    def test_distance(self):
        self.assertAlmostEquals(22.360679774997898, distance((0, 0), (10, 20)))
        self.assertAlmostEquals(22.360679774997898, distance((-1, -1), (9, 19)))
        self.assertAlmostEquals(22.360679774997898, distance((-1, 9), (9, 29)))
        self.assertAlmostEquals(22.360679774997898, distance((9, -1), (19, 19)))

if __name__ == '__main__':
    unittest.main()
