import unittest
from lands.generation import *
from lands.plates import *
import tempfile

def _sort(l):
	l2 = l
	l2.sort()
	return l2

class TestSerialization(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_protobuf_serialize_unserialize(self):
        w = world_gen("Dummy", 32, 16, 1, step=Step.get_by_name("full"))
        serialized = w.protobuf_serialize()
        unserialized = World.protobuf_unserialize(serialized)
        self.assertEqual(w.elevation['data'],       unserialized.elevation['data'])
        self.assertEqual(w.elevation['thresholds'], unserialized.elevation['thresholds'])
        self.assertEqual(w.ocean,                   unserialized.ocean)
        self.assertEqual(w.biome,                   unserialized.biome)
        self.assertEqual(w.humidity,                unserialized.humidity)
        self.assertEqual(w.irrigation,              unserialized.irrigation)
        self.assertEqual(w.permeability,            unserialized.permeability)
        self.assertEqual(w.watermap,                unserialized.watermap)
        self.assertEqual(w.precipitation,           unserialized.precipitation)
        self.assertEqual(w.temperature,             unserialized.temperature)
        self.assertEqual(w.sea_depth,               unserialized.sea_depth)
        self.assertEquals(w.seed,                   unserialized.seed)
        self.assertEquals(w.n_plates,               unserialized.n_plates)
        self.assertEquals(w.ocean_level,            unserialized.ocean_level)
        self.assertEquals(w.step,                   unserialized.step)
        self.assertEqual(_sort(dir(w)), _sort(dir(unserialized)))
        self.assertEqual(w, unserialized)


if __name__ == '__main__':
    unittest.main()