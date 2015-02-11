__author__ = 'Federico Tomassetti'

import unittest
from lands.biome import *
from lands.draw import _biome_colors

class TestDraw(unittest.TestCase):

    def setUp(self):
        pass

    def test_biome_colors(self):
        self.assertEqual(Biome.all_names(), _biome_colors.keys().sort())


if __name__ == '__main__':
    unittest.main()
