import random
import time
from noise import snoise2

from worldengine.simulations.basic import find_threshold_f
from worldengine.common import get_verbose


class PrecipitationSimulation(object):

    @staticmethod
    def is_applicable(world):
        return not world.has_precipitations()

    def execute(self, world, seed):
        if get_verbose():
            start_time = time.time()
        pre_calculated = self._calculate(seed, world.width, world.height)
        ths = [
            ('low', find_threshold_f(pre_calculated, 0.75, world.ocean)),
            ('med', find_threshold_f(pre_calculated, 0.3, world.ocean)),
            ('hig', None)
        ]
        world.set_precipitation(pre_calculated, ths)
        if get_verbose():
            elapsed_time = time.time() - start_time
            print(
                "...precipitations calculated. Elapsed time %f  seconds."
                % elapsed_time)

    @staticmethod
    def _calculate(seed, width, height):
        """Precipitation is a value in [-1,1]"""
        border = width / 4
        random.seed(seed * 13)
        base = random.randint(0, 4096)
        precipitations = [[0 for x in range(width)] for y in range(height)]
        # TODO: replace with numpy

        octaves = 6
        freq = 64.0 * octaves

        for y in range(height):
            y_scaled = float(y) / height
            latitude_factor = 1.0 - (abs(y_scaled - 0.5) * 2)
            for x in range(width):
                n = snoise2(x / freq, y / freq, octaves, base=base)

                # Added to allow noise pattern to wrap around right and left.
                if x < border:
                    n = (snoise2(x / freq, y / freq, octaves,
                                 base=base) * x / border) + (
                        snoise2((x + width) / freq, y / freq, octaves,
                                base=base) * (border - x) / border)

                precipitation = (latitude_factor + n * 4) / 5.0
                precipitations[y][x] = precipitation

        return precipitations
