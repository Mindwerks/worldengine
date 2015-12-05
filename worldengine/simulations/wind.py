from worldengine.simulations.basic import find_threshold_f
import numpy


class WindSimulation(object):

    @staticmethod
    def is_applicable(world):
        return not world.has_wind()

    def execute(self, world, seed):
        assert seed is not None
        data = self._wind(world, 1.5)
        world.set_wind(data)

    @staticmethod
    def _wind(world, distorsion_factor):
        print('WIIIIND')
        print('WIIIIND')
        print('WIIIIND')
        return None
