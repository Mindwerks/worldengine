import unittest
from lands.geo import *

class TestGeo(unittest.TestCase):

    def setUp(self):
        pass

    def test_scale_up(self):
        original_map = [
            [1, 2],
            [3, 4]
        ]
        expected_map = [
            [1.0,  1.33, 1.67,  2.0],
            [1.67, 2.0,  2.33, 2.67],
            [2.33, 2.67, 3.0,  3.33],
            [3.0,  3.67, 3.66,  4.0]
        ]
        actual_scaled_map = scale(original_map, 4, 4)
        for y in xrange(3):
            for x in xrange(3):
                self.assertAlmostEqual(expected_map[y][x], actual_scaled_map[y][x], places=2)

if __name__ == '__main__':
    unittest.main()