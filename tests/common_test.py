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

if __name__ == '__main__':
    unittest.main()
