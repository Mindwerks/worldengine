__author__ = 'Federico Tomassetti'

import unittest
from lands.biome import *


class TestBiome(unittest.TestCase):

    def setUp(self):
        pass

    def test_biome_by_name(self):
        self.assertRaises(Exception, Biome.by_name, "unexisting biome")
        self.assertIsInstance(Biome.by_name("ocean"), Ocean)

    def test_name(self):
        self.assertEqual("ocean", Ocean().name())
        self.assertEqual("polar desert", PolarDesert().name())
        self.assertEqual("subpolar dry tundra", SubpolarDryTundra().name())
        self.assertEqual("cool temperate moist forest", CoolTemperateMoistForest().name())


    @staticmethod
    def name():
        return 'cool temperate moist forest'


if __name__ == '__main__':
    unittest.main()
