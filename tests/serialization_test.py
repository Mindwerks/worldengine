import unittest
import tempfile
import os

from worldengine.plates import Step, world_gen
from worldengine.model.world import World
from worldengine.common import _equal
from worldengine.hdf5_serialization import save_world_to_hdf5, load_world_to_hdf5

try:  # are we python3?
    set
except NameError: # apparently not.
    from sets import Set as set


class TestSerialization(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_protobuf_serialize_unserialize(self):
        w = world_gen("Dummy", 32, 16, 1, step=Step.get_by_name("full"))
        serialized = w.protobuf_serialize()
        unserialized = World.protobuf_unserialize(serialized)
        self.assertEqual(set(w.layers.keys()), set(unserialized.layers.keys()))
        for l in w.layers.keys():
            self.assertEqual(w.layers[l], unserialized.layers[l], "Comparing %s" % l)
        self.assertTrue(_equal(w.ocean_level,       unserialized.ocean_level))
        self.assertEquals(w.seed,                   unserialized.seed)
        self.assertEquals(w.n_plates,               unserialized.n_plates)
        self.assertEquals(w.step,                   unserialized.step)
        self.assertEqual(sorted(dir(w)),            sorted(dir(unserialized)))
        self.assertEqual(w, unserialized)

    def test_hdf5_serialize_unserialize(self):
        filename = None
        try:
            w = world_gen("Dummy", 32, 16, 1, step=Step.get_by_name("full"))
            f = tempfile.NamedTemporaryFile(delete=False)
            f.close()
            filename = f.name
            serialized = save_world_to_hdf5(w, filename)
            unserialized = load_world_to_hdf5(filename)
            self.assertEqual(set(w.layers.keys()), set(unserialized.layers.keys()))
            self.assertEqual(w.layers['humidity'].quantiles, unserialized.layers['humidity'].quantiles)
            for l in w.layers.keys():
                self.assertEqual(w.layers[l], unserialized.layers[l], "Comparing %s" % l)
            self.assertTrue(_equal(w.ocean_level,       unserialized.ocean_level))
            self.assertEquals(w.seed,                   unserialized.seed)
            self.assertEquals(w.n_plates,               unserialized.n_plates)
            self.assertEquals(w.step,                   unserialized.step)
            self.assertEqual(sorted(dir(w)),            sorted(dir(unserialized)))
            #self.assertEqual(w, unserialized)
        finally:
            if filename:
                os.remove(filename)

if __name__ == '__main__':
    unittest.main()
