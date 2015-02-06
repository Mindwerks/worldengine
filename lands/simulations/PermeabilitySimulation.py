__author__ = 'Federico Tomassetti'

from lands.simulations.basic import *
import random

class PermeabilitySimulation(object):

    def is_applicable(self, world):
        return not world.has_permeability()

    def execute(self, world, seed):
        perm = self._calculate(seed, world.width, world.height)
        perm_th = [
            ('low', find_threshold_f(perm, 0.75, world.ocean)),
            ('med', find_threshold_f(perm, 0.25, world.ocean)),
            ('hig', None)
        ]
        world.set_permeability(perm, perm_th)

    def _calculate(self, seed, width, height):
        random.seed(seed * 37)
        base = random.randint(0, 4096)
        perm = [[0 for x in xrange(width)] for y in xrange(height)]

        from noise import snoise2

        octaves = 6
        freq = 64.0 * octaves

        for y in range(0, height):
            yscaled = float(y) / height
            for x in range(0, width):
                n = snoise2(x / freq, y / freq, octaves, base=base)
                t = n
                perm[y][x] = t

        return perm
