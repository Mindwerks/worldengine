import unittest
from worldengine.biome import Biome, Ocean, PolarDesert, SubpolarDryTundra, \
    CoolTemperateMoistForest, biome_name_to_index, biome_index_to_name
from worldengine.simulations.biome import BiomeSimulation
from worldengine.world import World
import os


class TestBiome(unittest.TestCase):

    def setUp(self):
        tests_dir = os.path.dirname(os.path.realpath(__file__))
        self.tests_data_dir = os.path.abspath(os.path.join(
            tests_dir, "../../worldengine-data/tests/data"))
        pass

    def test_biome_by_name(self):
        self.assertRaises(Exception, Biome.by_name, "unexisting biome")
        self.assertTrue(isinstance(Biome.by_name("ocean"), Ocean))

    def test_name(self):
        self.assertEqual("ocean", Ocean().name())
        self.assertEqual("polar desert", PolarDesert().name())
        self.assertEqual("subpolar dry tundra", SubpolarDryTundra().name())
        self.assertEqual("cool temperate moist forest", CoolTemperateMoistForest().name())

    def test_biome_name_to_index(self):
        self.assertRaises(Exception, biome_name_to_index, "unexisting biome")

        # We do not want these values to change in the future, otherwise the world saved
        # will be not loaded correctly
        self.assertEqual(0, biome_name_to_index('boreal desert'))
        self.assertEqual(1, biome_name_to_index('boreal dry scrub'))
        self.assertEqual(2, biome_name_to_index('boreal moist forest'))
        self.assertEqual(3, biome_name_to_index('boreal rain forest'))
        self.assertEqual(4, biome_name_to_index('boreal wet forest'))
        self.assertEqual(5, biome_name_to_index('cool temperate desert'))
        self.assertEqual(6, biome_name_to_index('cool temperate desert scrub'))
        self.assertEqual(7, biome_name_to_index('cool temperate moist forest'))
        self.assertEqual(8, biome_name_to_index('cool temperate rain forest'))
        self.assertEqual(9, biome_name_to_index('cool temperate steppe'))
        self.assertEqual(10, biome_name_to_index('cool temperate wet forest'))
        self.assertEqual(11, biome_name_to_index('ice'))
        self.assertEqual(12, biome_name_to_index('ocean'))
        self.assertEqual(13, biome_name_to_index('polar desert'))
        self.assertEqual(14, biome_name_to_index('sea'))
        self.assertEqual(15, biome_name_to_index('subpolar dry tundra'))
        self.assertEqual(16, biome_name_to_index('subpolar moist tundra'))
        self.assertEqual(17, biome_name_to_index('subpolar rain tundra'))
        self.assertEqual(18, biome_name_to_index('subpolar wet tundra'))
        self.assertEqual(19, biome_name_to_index('subtropical desert'))
        self.assertEqual(20, biome_name_to_index('subtropical desert scrub'))
        self.assertEqual(21, biome_name_to_index('subtropical dry forest'))
        self.assertEqual(22, biome_name_to_index('subtropical moist forest'))
        self.assertEqual(23, biome_name_to_index('subtropical rain forest'))
        self.assertEqual(24, biome_name_to_index('subtropical thorn woodland'))
        self.assertEqual(25, biome_name_to_index('subtropical wet forest'))
        self.assertEqual(26, biome_name_to_index('tropical desert'))
        self.assertEqual(27, biome_name_to_index('tropical desert scrub'))
        self.assertEqual(28, biome_name_to_index('tropical dry forest'))
        self.assertEqual(29, biome_name_to_index('tropical moist forest'))
        self.assertEqual(30, biome_name_to_index('tropical rain forest'))
        self.assertEqual(31, biome_name_to_index('tropical thorn woodland'))
        self.assertEqual(32, biome_name_to_index('tropical very dry forest'))
        self.assertEqual(33, biome_name_to_index('tropical wet forest'))
        self.assertEqual(34, biome_name_to_index('warm temperate desert'))
        self.assertEqual(35, biome_name_to_index('warm temperate desert scrub'))
        self.assertEqual(36, biome_name_to_index('warm temperate dry forest'))
        self.assertEqual(37, biome_name_to_index('warm temperate moist forest'))
        self.assertEqual(38, biome_name_to_index('warm temperate rain forest'))
        self.assertEqual(39, biome_name_to_index('warm temperate thorn scrub'))
        self.assertEqual(40, biome_name_to_index('warm temperate wet forest'))

    def test_biome_index_to_name(self):
        self.assertRaises(Exception, biome_index_to_name, -1)
        self.assertRaises(Exception, biome_index_to_name, 41)
        self.assertRaises(Exception, biome_index_to_name, 100)

        # We do not want these values to change in the future, otherwise the world saved
        # will be not loaded correctly
        self.assertEqual('boreal desert', biome_index_to_name(0))
        self.assertEqual('boreal dry scrub', biome_index_to_name(1))
        self.assertEqual('boreal moist forest', biome_index_to_name(2))
        self.assertEqual('boreal rain forest', biome_index_to_name(3))
        self.assertEqual('boreal wet forest', biome_index_to_name(4))
        self.assertEqual('cool temperate desert', biome_index_to_name(5))
        self.assertEqual('cool temperate desert scrub', biome_index_to_name(6))
        self.assertEqual('cool temperate moist forest', biome_index_to_name(7))
        self.assertEqual('cool temperate rain forest', biome_index_to_name(8))
        self.assertEqual('cool temperate steppe', biome_index_to_name(9))
        self.assertEqual('cool temperate wet forest', biome_index_to_name(10))
        self.assertEqual('ice', biome_index_to_name(11))
        self.assertEqual('ocean', biome_index_to_name(12))
        self.assertEqual('polar desert', biome_index_to_name(13))
        self.assertEqual('sea', biome_index_to_name(14))
        self.assertEqual('subpolar dry tundra', biome_index_to_name(15))
        self.assertEqual('subpolar moist tundra', biome_index_to_name(16))
        self.assertEqual('subpolar rain tundra', biome_index_to_name(17))
        self.assertEqual('subpolar wet tundra', biome_index_to_name(18))
        self.assertEqual('subtropical desert', biome_index_to_name(19))
        self.assertEqual('subtropical desert scrub', biome_index_to_name(20))
        self.assertEqual('subtropical dry forest', biome_index_to_name(21))
        self.assertEqual('subtropical moist forest', biome_index_to_name(22))
        self.assertEqual('subtropical rain forest', biome_index_to_name(23))
        self.assertEqual('subtropical thorn woodland', biome_index_to_name(24))
        self.assertEqual('subtropical wet forest', biome_index_to_name(25))
        self.assertEqual('tropical desert', biome_index_to_name(26))
        self.assertEqual('tropical desert scrub', biome_index_to_name(27))
        self.assertEqual('tropical dry forest', biome_index_to_name(28))
        self.assertEqual('tropical moist forest', biome_index_to_name(29))
        self.assertEqual('tropical rain forest', biome_index_to_name(30))
        self.assertEqual('tropical thorn woodland', biome_index_to_name(31))
        self.assertEqual('tropical very dry forest', biome_index_to_name(32))
        self.assertEqual('tropical wet forest', biome_index_to_name(33))
        self.assertEqual('warm temperate desert', biome_index_to_name(34))
        self.assertEqual('warm temperate desert scrub', biome_index_to_name(35))
        self.assertEqual('warm temperate dry forest', biome_index_to_name(36))
        self.assertEqual('warm temperate moist forest', biome_index_to_name(37))
        self.assertEqual('warm temperate rain forest', biome_index_to_name(38))
        self.assertEqual('warm temperate thorn scrub', biome_index_to_name(39))
        self.assertEqual('warm temperate wet forest', biome_index_to_name(40))

    def test_locate_biomes(self):
        w = World.open_protobuf("%s/seed_28070.world" % self.tests_data_dir)
        cm, biome_cm = BiomeSimulation().execute(w, 28070)

    @staticmethod
    def name():
        return 'cool temperate moist forest'


if __name__ == '__main__':
    unittest.main()
