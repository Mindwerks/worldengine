import unittest
import numpy
from worldengine import astar
from worldengine.common import _equal


class TestCommon(unittest.TestCase):

    def test_traversal(self):
        test_map = numpy.zeros((20, 20))
        line = numpy.array(20)
        line.fill(1.0)
        test_map[10, :] = line
        test_map[10, 18] = 0.0
        path_data = numpy.array([[0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7], [0, 8], [0, 9],
                                 [1, 9], [2, 9], [3, 9], [4, 9], [5, 9], [6, 9], [7, 9], [8, 9], [9, 9],
                                 [10, 9], [11, 9], [12, 9], [13, 9], [14, 9], [15, 9], [16, 9], [17, 9],
                                 [18, 9], [18, 10], [18, 11], [18, 12], [18, 13], [18, 14], [18, 15],
                                 [18, 16], [18, 17], [18, 18], [18, 19], [19, 19]])
        shortest_path = astar.PathFinder().find(test_map, [0, 0], [19, 19])
        self.assertTrue(_equal(path_data, numpy.array(shortest_path)))

if __name__ == '__main__':
    unittest.main()
