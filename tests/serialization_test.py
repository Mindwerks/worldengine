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
        self.assertEqual(w, unserialized)


if __name__ == '__main__':
    unittest.main()