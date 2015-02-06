__author__ = 'Federico Tomassetti'

from lands.simulations.basic import *
import math

class IrrigationSimulation(object):

    def is_applicable(self, world):
        return world.has_watermap() and (not world.has_irrigation())

    def execute(self, world, seed):
        world.irrigation = self._calculate(world)

    def _calculate(self, world):
        width = world.width
        height = world.height

        values = [[0 for x in xrange(width)] for y in xrange(height)]
        radius = 10

        for y in xrange(height):
            for x in xrange(width):
                if world.is_land((x, y)):
                    for dy in range(-radius, radius + 1):
                        if (y + dy) >= 0 and (y + dy) < world.height:
                            for dx in range(-radius, radius + 1):
                                if (x + dx) >= 0 and (x + dx) < world.width:
                                    dist = math.sqrt(dx ** 2 + dy ** 2)
                                    values[y + dy][x + dx] += world.watermap['data'][y][x] / (math.log(dist + 1) + 1)

        return values
