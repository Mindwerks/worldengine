import numpy
import unittest
from worldengine.basic_map_operations import distance, index_of_nearest


class TestBasicMapOperations(unittest.TestCase):

    def setUp(self):
        pass

    def test_distance(self):
        self.assertAlmostEquals(22.360679774997898, distance((0, 0), (10, 20)))
        self.assertAlmostEquals(22.360679774997898, distance((-1, -1), (9, 19)))
        self.assertAlmostEquals(22.360679774997898, distance((-1, 9), (9, 29)))
        self.assertAlmostEquals(22.360679774997898, distance((9, -1), (19, 19)))

    def test_index_of_nearest(self):
        self.assertTrue(index_of_nearest((0, 0), []) is None)
        self.assertEqual(0, index_of_nearest(
            (0, 0), [(0, 0), (10, 10), (7, 7), (-5, -5), (-2, 7)]))
        self.assertEqual(3, index_of_nearest(
            (-4, -4), [(0, 0), (10, 10), (7, 7), (-5, -5), (-2, 7)]))
        self.assertEqual(3, index_of_nearest(
            (-100, -100), [(0, 0), (10, 10), (7, 7), (-5, -5), (-2, 7)]))
        self.assertEqual(3, index_of_nearest(
            (-100.0, -100.0), [(0, 0), (10, 10), (7, 7), (-5, -5), (-2, 7)]))

if __name__ == '__main__':
    unittest.main()
