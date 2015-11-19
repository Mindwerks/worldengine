import unittest
import tempfile
import os

from worldengine.plates import Step, world_gen
from worldengine.model.world import World
from worldengine.common import _equal
from worldengine.hdf5_serialization import save_world_to_hdf5, load_world_to_hdf5


class TestSerialization(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_protobuf_serialize_unserialize(self):
        w = world_gen("Dummy", 32, 16, 1, step=Step.get_by_name("full"))
        serialized = w.protobuf_serialize()
        unserialized = World.protobuf_unserialize(serialized)
        self.assertEqual(w.layers.keys(), unserialized.layers.keys())
        for l in w.layers.keys():
            self.assertEqual(w.layers[l], unserialized.layers[l])
        self.assertTrue(_equal(w.humidity,          unserialized.humidity))
        self.assertTrue(_equal(w.watermap,          unserialized.watermap))
        self.assertTrue(_equal(w.precipitation,     unserialized.precipitation))
        self.assertTrue(_equal(w.temperature,       unserialized.temperature))
        self.assertTrue(_equal(w.ocean_level,       unserialized.ocean_level))
        self.assertTrue(_equal(w.lake_map,          unserialized.lake_map))
        self.assertTrue(_equal(w.river_map,         unserialized.river_map))
        self.assertTrue(_equal(w.icecap,            unserialized.icecap))
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
            self.assertEqual(w.layers.keys(), unserialized.layers.keys())
            for l in w.layers.keys():
                self.assertEqual(w.layers[l], unserialized.layers[l])
            self.assertTrue(_equal(w.humidity['quantiles'], unserialized.humidity['quantiles']))
            self.assertTrue(_equal(w.humidity['data'],  unserialized.humidity['data']))
            self.assertTrue(_equal(w.humidity,          unserialized.humidity))
            self.assertTrue(_equal(w.watermap,          unserialized.watermap))
            self.assertTrue(_equal(w.precipitation['thresholds'], unserialized.precipitation['thresholds']))
            self.assertTrue(_equal(w.precipitation['data'], unserialized.precipitation['data']))
            self.assertTrue(_equal(w.precipitation,     unserialized.precipitation))
            self.assertTrue(_equal(w.temperature,       unserialized.temperature))
            self.assertTrue(_equal(w.ocean_level,       unserialized.ocean_level))
            self.assertTrue(_equal(w.lake_map,          unserialized.lake_map))
            self.assertTrue(_equal(w.river_map,         unserialized.river_map))
            self.assertTrue(_equal(w.icecap,            unserialized.icecap))
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
