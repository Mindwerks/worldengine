import os
import tempfile
import unittest

from worldengine.common import _equal
from worldengine.hdf5_serialization import load_world_to_hdf5, save_world_to_hdf5
from worldengine.model.world import World
from worldengine.plates import Step, world_gen


class TestSerialization(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_protobuf_serialize_unserialize(self):
        w = world_gen("Dummy", 32, 16, 1, step=Step.get_by_name("full"))
        serialized = w.protobuf_serialize()
        unserialized = World.protobuf_unserialize(serialized)
        self.assertEqual(set(w.layers.keys()), set(unserialized.layers.keys()))
        for layer in w.layers.keys():
            self.assertEqual(w.layers[layer], unserialized.layers[layer], "Comparing %s" % layer)
        self.assertTrue(_equal(w.ocean_level, unserialized.ocean_level))
        self.assertEqual(w.seed, unserialized.seed)
        self.assertEqual(w.n_plates, unserialized.n_plates)
        self.assertEqual(w.step, unserialized.step)
        self.assertEqual(sorted(dir(w)), sorted(dir(unserialized)))
        self.assertEqual(w, unserialized)

    def test_hdf5_serialize_unserialize(self):
        filename = None
        try:
            w = world_gen("Dummy", 32, 16, 1, step=Step.get_by_name("full"))
            f = tempfile.NamedTemporaryFile(delete=False)
            f.close()
            filename = f.name
            save_world_to_hdf5(w, filename)
            unserialized = load_world_to_hdf5(filename)
            self.assertEqual(set(w.layers.keys()), set(unserialized.layers.keys()))
            self.assertEqual(w.layers["humidity"].quantiles, unserialized.layers["humidity"].quantiles)
            for layer in w.layers.keys():
                self.assertEqual(w.layers[layer], unserialized.layers[layer], "Comparing %s" % layer)
            self.assertTrue(_equal(w.ocean_level, unserialized.ocean_level))
            self.assertEqual(w.seed, unserialized.seed)
            self.assertEqual(w.n_plates, unserialized.n_plates)
            self.assertEqual(w.step, unserialized.step)
            self.assertEqual(sorted(dir(w)), sorted(dir(unserialized)))
            # self.assertEqual(w, unserialized)
        finally:
            if filename:
                os.remove(filename)


if __name__ == "__main__":
    unittest.main()
