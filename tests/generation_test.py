import unittest

from worldengine.plates import Step, center_land, world_gen
from worldengine.model.world import World
from tests.draw_test import TestBase


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


if __name__ == '__main__':
    unittest.main()
