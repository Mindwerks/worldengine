import numpy

from worldengine.simplex import snoise2
from worldengine.simulations.basic import find_threshold_f


class PermeabilitySimulation:
    @staticmethod
    def is_applicable(world):
        return not world.has_permeability()

    def execute(self, world, seed):
        perm = self._calculate(seed, world.width, world.height)
        ocean = world.layers["ocean"].data
        perm_th = [
            ("low", find_threshold_f(perm, 0.75, ocean)),
            ("med", find_threshold_f(perm, 0.25, ocean)),
            ("hig", None),
        ]
        world.permeability = (perm, perm_th)

    @staticmethod
    def _calculate(seed, width, height):
        rng = numpy.random.RandomState(seed)  # create our own random generator
        base = rng.randint(0, 4096)

        octaves = 6
        freq = 64.0 * octaves

        x = numpy.arange(width)
        y = numpy.arange(height).reshape(-1, 1)
        return snoise2(x / freq, y / freq, octaves, base=base).astype(float)
