__author__ = 'Federico Tomassetti'

from lands.simulations.basic import *
import random

class TemperatureSimulation(object):

    def is_applicable(self, world):
        return not world.has_temperature()

    def execute(self, world, seed):
        e = world.elevation['data']
        ml = world.start_mountain_th()
        ocean = world.ocean

        t = self._calculate(world, seed, e, ml)
        t_th = [
            ('polar', find_threshold_f(t, 0.90, ocean)),
            ('alpine', find_threshold_f(t, 0.76, ocean)),
            ('boreal', find_threshold_f(t, 0.59, ocean)),
            ('cool', find_threshold_f(t, 0.38, ocean)),
            ('warm', find_threshold_f(t, 0.26, ocean)),
            ('subtropical', find_threshold_f(t, 0.14, ocean)),
            ('tropical', None)
        ]
        world.set_temperature(t, t_th)


    def _calculate(self, world, seed, elevation, mountain_level):
        width = world.width
        height = world.height

        random.seed(seed * 7)
        base = random.randint(0, 4096)
        temp = [[0 for x in xrange(width)] for y in xrange(height)]

        from noise import snoise2

        border = width / 4
        octaves = 6
        freq = 16.0 * octaves

        for y in range(0, height):
            yscaled = float(y) / height
            latitude_factor = 1.0 - (abs(yscaled - 0.5) * 2)
            for x in range(0, width):
                n = snoise2(x / freq, y / freq, octaves, base=base)

                #Added to allow noise pattern to wrap around right and left.
                if x <= border:
                    n = (snoise2(x / freq, y / freq, octaves, base=base) * x / border) \
                        + (snoise2((x+width) / freq, y / freq, octaves, base=base) * (border-x)/border)

                t = (latitude_factor * 3 + n * 2) / 5.0
                if elevation[y][x] > mountain_level:
                    if elevation[y][x] > (mountain_level + 29):
                        altitude_factor = 0.033
                    else:
                        altitude_factor = 1.00 - (float(elevation[y][x] - mountain_level) / 30)
                    t *= altitude_factor
                temp[y][x] = t

        return temp

