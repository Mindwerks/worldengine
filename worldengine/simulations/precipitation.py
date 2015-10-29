import random
import time
import numpy
import math
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
        pre_calculated = self._calculate(seed, world)
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
    def _calculate(seed, world):
        """Precipitation is a value in [-1,1]"""
        curve_gamma = 1.25
        curve_bonus = .2
        height = world.height
        width = world.width
        border = width / 4
        random.seed(seed * 13)
        base = random.randint(0, 4096)
        precipitations = numpy.zeros((height, width), dtype=float)

        octaves = 6
        freq = 64.0 * octaves

        for y in range(height):#TODO: numpy
            y_scaled = float(y) / height
            n_scale = 1024 / float(height)
            latitude_factor = 1.0 - (abs(y_scaled - 0.5) * 2)
            for x in range(width):
                n = snoise2((x * n_scale) / freq, (y * n_scale) / freq, octaves, base=base)

                # Added to allow noise pattern to wrap around right and left.
                if x < border:
                    n = (snoise2( (x * n_scale) / freq, (y * n_scale) / freq, octaves,
                                 base=base) * x / border) + (
                        snoise2(( (x * n_scale) + width) / freq, (y * n_scale) / freq, octaves,
                                base=base) * (border - x) / border)

                precipitations[y, x] = n
        min_precip = None
        max_precip = None
        min_temp = None
        max_temp = None

        #find ranges
        for y in range(height):#TODO: numpy
            for x in range(width):
                t = world.temperature_at((x, y))
                p = precipitations[y, x]
                if min_precip is None or p < min_precip:
                    min_precip = p
                if max_precip is None or p > max_precip:
                    max_precip = p
                if min_temp is None or t < min_temp:
                    min_temp = t
                if max_temp is None or t > max_temp:
                    max_temp = t
        precip_delta = (max_precip - min_precip)
        temp_delta = (max_temp - min_temp)

        #modify precipitation based on temperature
        for y in range(height):
            for x in range(width):
                t = (world.temperature_at((x, y)) - min_temp) / temp_delta
                p = (precipitations[y, x] - min_precip) / precip_delta
                precipitations[y, x] = (2 * p * (math.pow((t),curve_gamma) + curve_bonus))

        #Renormalize temperatures because the temperature 
        #changes will probably not fully extend from -1 to 1.
        min_temp = None
        max_temp = None
        for y in range(height):
            for x in range(width):
                p = precipitations[y, x]
                if min_precip is None or p < min_precip:
                    min_precip = p
                if max_precip is None or p > max_precip:
                    max_precip = p
        precip_delta = (max_precip - min_precip)
        for y in range(height):
            for x in range(width):
                precipitations[y, x] = (2 * ((precipitations[y, x] - min_precip) / precip_delta)) - 1
                
        return precipitations
