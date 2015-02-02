import unittest
from lands.geo import *
from lands.plates import *
from lands.generator import *
import tempfile

class TestSerialization(unittest.TestCase):

    def setUp(self):
        pass

    def test_protobuf_serialize_unserialize(self):
        w = world_gen("Dummy", 1, False, 32, 16, Step.get_by_name("full"))
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
        self.assertEqual(w, unserialized)


if __name__ == '__main__':
    unittest.main()