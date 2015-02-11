__author__ = 'Federico Tomassetti'

import unittest
from lands.common import *


class TestCommon(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_and_set_verbose(self):
        self.assertEqual(False, get_verbose(), "By default verbose should be set to False")
        set_verbose(True)
        self.assertEqual(True, get_verbose())
        set_verbose(False)
        self.assertEqual(False, get_verbose())

    def test_matrix_min_and_max(self):
        m1 = [
            [-0.8, -0.5, 1.0, 2.6],
            [-0.8, -1.5, 8.8, 2.7]
        ]
        m2 = []
        m3 = [[], []]
        m4 = [[0.0]]
        self.assertEqual((-1.5, 8.8), matrix_min_and_max(m1))
        self.assertEqual((None, None), matrix_min_and_max(m2))
        self.assertEqual((None, None), matrix_min_and_max(m3))
        self.assertEqual((0.0, 0.0), matrix_min_and_max(m4))


if __name__ == '__main__':
    unittest.main()
