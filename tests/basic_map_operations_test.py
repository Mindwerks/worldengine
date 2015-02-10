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


if __name__ == '__main__':
    unittest.main()
