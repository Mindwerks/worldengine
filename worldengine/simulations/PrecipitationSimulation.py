import random
import time
from noise import snoise2

from worldengine.simulations.basic import *
from worldengine.common import *

class PrecipitationSimulation(object):

    def is_applicable(self, world):
        return not world.has_precipitations()

    def execute(self, world, seed):
        if get_verbose():
            start_time = time.time()
        prec = self._calculate(seed, world.width, world.height)
        ths = [
            ('low', find_threshold_f(prec, 0.75, world.ocean)),
            ('med', find_threshold_f(prec, 0.3, world.ocean)),
            ('hig', None)
        ]
        world.set_precipitation(prec, ths)
        if get_verbose():
            elapsed_time = time.time() - start_time
            print("...precipitations calculated. Elapsed time %f  seconds." % elapsed_time)


    def _calculate(self, seed, width, height):
        """"Precipitation is a value in [-1,1]"""
        border = width / 4
        random.seed(seed * 13)
        base = random.randint(0, 4096)
        precipitations = [[0 for x in range(width)] for y in range(height)]

        octaves = 6
        freq = 64.0 * octaves

        for y in range(height):
            yscaled = float(y) / height
            latitude_factor = 1.0 - (abs(yscaled - 0.5) * 2)
            for x in range(width):
                n = snoise2(x / freq, y / freq, octaves, base=base)

                # Added to allow noise pattern to wrap around right and left.
                if x < border:
                    n = (snoise2(x / freq, y / freq, octaves, base=base) * x / border) + (snoise2((x+width) / freq, y / freq, octaves, base=base) * (border-x)/border)

                prec = (latitude_factor + n * 4) / 5.0
                precipitations[y][x] = prec

        return precipitations
