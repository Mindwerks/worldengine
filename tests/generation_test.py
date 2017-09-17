import unittest

import numpy

from worldengine.plates import Step, center_land, world_gen
from worldengine.model.world import World, Size, GenerationParameters
from tests.draw_test import TestBase

from worldengine.generation import sea_depth
from worldengine.common import anti_alias


class TestGeneration(TestBase):

    def setUp(self):
        super(TestGeneration, self).setUp()

    def test_world_gen_does_not_explode_badly(self):
        # FIXME remove me when proper tests are in place
        # Very stupid test that just verify nothing explode badly
        world_gen("Dummy", 32, 16, 1, step=Step.get_by_name("full"))

    @staticmethod
    def _mean_elevation_at_borders(world):
        borders_total_elevation = 0.0
        for y in range(world.height):
            borders_total_elevation += world.elevation_at((0, y))
            borders_total_elevation += world.elevation_at((world.width - 1, y))
        for x in range(1, world.width - 1):
            borders_total_elevation += world.elevation_at((x, 0))
            borders_total_elevation += world.elevation_at((x, world.height - 1))

        n_cells_on_border = world.width * 2 + world.height * 2 - 4
        return borders_total_elevation / n_cells_on_border

    def test_center_land(self):
        w = World.open_protobuf("%s/seed_28070.world" % self.tests_data_dir)

        # We want to have less land than before at the borders
        el_before = TestGeneration._mean_elevation_at_borders(w)
        center_land(w)
        el_after = TestGeneration._mean_elevation_at_borders(w)
        self.assertTrue(el_after <= el_before)

    def test_sea_depth(self):
        ocean_level = 1.0
        extent = 11
        w = World("sea_depth", Size(extent,extent), 0, GenerationParameters(0, ocean_level, 0), None)

        ocean = numpy.full([extent,extent], True)
        ocean[5,5]=False

        elevation = numpy.zeros([extent,extent], float)
        elevation[5,5] = 2.0

        t = numpy.zeros([extent, extent])

        w.elevation = (elevation, t)
        w.ocean = ocean

        desired_result = numpy.asarray([0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, \
                                0.9, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.9, \
                                0.9, 0.7, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.7, 0.9, \
                                0.9, 0.7, 0.5, 0.3, 0.3, 0.3, 0.3, 0.3, 0.5, 0.7, 0.9, \
                                0.9, 0.7, 0.5, 0.3, 0.0, 0.0, 0.0, 0.3, 0.5, 0.7, 0.9, \
                                0.9, 0.7, 0.5, 0.3, 0.0, -1.0, 0.0, 0.3, 0.5, 0.7, 0.9, \
                                0.9, 0.7, 0.5, 0.3, 0.0, 0.0, 0.0, 0.3, 0.5, 0.7, 0.9, \
                                0.9, 0.7, 0.5, 0.3, 0.3, 0.3, 0.3, 0.3, 0.5, 0.7, 0.9, \
                                0.9, 0.7, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.7, 0.9, \
                                0.9, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.9, \
                                0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9])

        desired_result = desired_result.reshape([extent,extent])

        # this part is verbatim from the function. It's not part of the test
        # Some refactoring is in order to increase test quality
        desired_result = anti_alias(desired_result, 10)

        min_depth = desired_result.min()
        max_depth = desired_result.max()
        desired_result = (desired_result - min_depth) / (max_depth - min_depth)

        # end of verbatim part

        result = sea_depth(w, ocean_level)

        for y in range(extent):
            for x in range(extent):
                self.assertAlmostEqual(desired_result[y,x], result[y,x])

        


    


if __name__ == '__main__':
    unittest.main()
