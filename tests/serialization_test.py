import unittest
from worldengine.plates import Step, world_gen
from worldengine.world import World
from worldengine.common import _equal
import tempfile
import os

class TestSerialization(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_pickle_serialize_unserialize(self):
        w = world_gen("Dummy", 32, 16, 1, step=Step.get_by_name("full"))
        f = tempfile.NamedTemporaryFile(delete=False).name
        w.to_pickle_file(f)
        unserialized = World.from_pickle_file(f)
        os.remove(f)
        self.assertTrue(_equal(w.elevation['data'], unserialized.elevation['data']))
        self.assertEqual(w.elevation['thresholds'], unserialized.elevation['thresholds'])
        self.assertTrue(_equal(w.ocean,             unserialized.ocean))
        self.assertTrue(_equal(w.biome,             unserialized.biome))
        self.assertTrue(_equal(w.humidity,          unserialized.humidity))
        self.assertTrue(_equal(w.irrigation,        unserialized.irrigation))
        self.assertTrue(_equal(w.permeability,      unserialized.permeability))
        self.assertTrue(_equal(w.watermap,          unserialized.watermap))
        self.assertTrue(_equal(w.precipitation,     unserialized.precipitation))
        self.assertTrue(_equal(w.temperature,       unserialized.temperature))
        self.assertTrue(_equal(w.sea_depth,         unserialized.sea_depth))
        self.assertEquals(w.seed,                   unserialized.seed)
        self.assertEquals(w.n_plates,               unserialized.n_plates)
        self.assertTrue(_equal(w.ocean_level,       unserialized.ocean_level))
        self.assertTrue(_equal(w.lake_map,          unserialized.lake_map))
        self.assertTrue(_equal(w.river_map,         unserialized.river_map))
        self.assertEquals(w.step,                   unserialized.step)
        self.assertEqual(sorted(dir(w)),            sorted(dir(unserialized)))
        self.assertEqual(w, unserialized)

    def test_protobuf_serialize_unserialize(self):
        w = world_gen("Dummy", 32, 16, 1, step=Step.get_by_name("full"))
        serialized = w.protobuf_serialize()
        unserialized = World.protobuf_unserialize(serialized)
        self.assertTrue(_equal(w.elevation['data'], unserialized.elevation['data']))
        self.assertEqual(w.elevation['thresholds'], unserialized.elevation['thresholds'])
        self.assertTrue(_equal(w.ocean,             unserialized.ocean))
        self.assertTrue(_equal(w.biome,             unserialized.biome))
        self.assertTrue(_equal(w.humidity,          unserialized.humidity))
        self.assertTrue(_equal(w.irrigation,        unserialized.irrigation))
        self.assertTrue(_equal(w.permeability,      unserialized.permeability))
        self.assertTrue(_equal(w.watermap,          unserialized.watermap))
        self.assertTrue(_equal(w.precipitation,     unserialized.precipitation))
        self.assertTrue(_equal(w.temperature,       unserialized.temperature))
        self.assertTrue(_equal(w.sea_depth,         unserialized.sea_depth))
        self.assertEquals(w.seed,                   unserialized.seed)
        self.assertEquals(w.n_plates,               unserialized.n_plates)
        self.assertTrue(_equal(w.ocean_level,       unserialized.ocean_level))
        self.assertTrue(_equal(w.lake_map,          unserialized.lake_map))
        self.assertTrue(_equal(w.river_map,         unserialized.river_map))
        self.assertEquals(w.step,                   unserialized.step)
        self.assertEqual(sorted(dir(w)),            sorted(dir(unserialized)))
        self.assertEqual(w, unserialized)


if __name__ == '__main__':
    unittest.main()
