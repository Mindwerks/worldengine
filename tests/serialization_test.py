import unittest
import tempfile
import os
#from worldengine.step import Step
from worldengine.world import World
from worldengine.hdf5_serialization import save_world_to_hdf5, load_world_to_hdf5

try:  # are we python3?
    set
except NameError: # apparently not.
    from sets import Set as set


class TestSerialization(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_protobuf_serialize_unserialize(self):
        w = World("Dummy", 16, 16, seed=1)
        serialized = w.protobuf_serialize()
        unserialized = World.protobuf_unserialize(serialized)
        self.assertEqual(set(w.layers.keys()), set(unserialized.layers.keys()))
        for l in w.layers.keys():
            self.assertEqual(w.layers[l].all(), unserialized.layers[l].all())
        self.assertEqual(w.ocean_level,       unserialized.ocean_level)
        self.assertEqual(w.seed,                   unserialized.seed)
        self.assertEqual(w.number_of_plates,       unserialized.number_of_plates)
        self.assertEqual(sorted(dir(w)),            sorted(dir(unserialized)))
        self.assertEqual(w, unserialized)

    def test_hdf5_serialize_unserialize(self):
        filename = None
        try:
            w = World("Dummy", 16, 16,1)
            f = tempfile.NamedTemporaryFile(delete=False)
            f.close()
            filename = f.name
            serialized = save_world_to_hdf5(w, filename)
            unserialized = load_world_to_hdf5(filename)
            self.assertEqual(set(w.layers.keys()), set(unserialized.layers.keys()))
            self.assertEqual(w.layers['humidity'].quantiles, unserialized.layers['humidity'].quantiles)
            for l in w.layers.keys():
                self.assertEqual(w.layers[l].all(), unserialized.layers[l].all())
            self.assertEqual(w.ocean_level,       unserialized.ocean_level)
            self.assertEqual(w.seed,                   unserialized.seed)
            self.assertEqual(w.number_of_plates,      unserialized.number_of_plates)
            self.assertEqual(sorted(dir(w)),            sorted(dir(unserialized)))
        finally:
            if filename:
                os.remove(filename)

                
if __name__ == '__main__':
    unittest.main()
