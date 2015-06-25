from worldengine.simulations.basic import find_threshold_f
import random


class PermeabilitySimulation(object):

    @staticmethod
    def is_applicable(world):
        return not world.has_permeability()

    def execute(self, world, seed):
        perm = self._calculate(seed, world.width, world.height)
        perm_th = [
            ('low', find_threshold_f(perm, 0.75, world.ocean)),
            ('med', find_threshold_f(perm, 0.25, world.ocean)),
            ('hig', None)
        ]
        world.set_permeability(perm, perm_th)

    @staticmethod
    def _calculate(seed, width, height):
        random.seed(seed * 37)
        base = random.randint(0, 4096)
        perm = [[0 for x in xrange(width)] for y in xrange(height)]  # TODO: replace with numpy

        from noise import snoise2

        octaves = 6
        freq = 64.0 * octaves

        for y in range(0, height):
            # yscaled = float(y) / height  # TODO: what is this?
            for x in range(0, width):
                n = snoise2(x / freq, y / freq, octaves, base=base)
                t = n
                perm[y][x] = t

        return perm
