from worldengine.simulations.basic import *
import math
import numpy

# Direction
NORTH       = [0, -1]
NORTH_EAST  = [1, -1]
EAST        = [1, 0]
SOUTH_EAST  = [1, 1]
SOUTH       = [0, 1]
SOUTH_WEST  = [-1, 1]
WEST        = [-1, 0]
NORTH_WEST  = [-1, -1]
CENTER      = [0, 0]

DIR_NEIGHBORS           = [NORTH, EAST, SOUTH, WEST]
DIR_NEIGHBORS_CENTER    = [CENTER, NORTH, EAST, SOUTH, WEST]

overflow = lambda value, maxValue: value % maxValue

class ErosionSimulation(object):

    def __init__(self):
        self.wrap = True

    def is_applicable(self, world):
        return world.has_precipitations()

    def execute(self, world, seed):
        waterPath = numpy.zeros((world.width, world.height), dtype=int)
        self.findWaterFlow(world, waterPath)

    def findWaterFlow(self, world, waterPath):
        '''Find the flow direction for each cell in heightmap'''
        # iterate through each cell
        for x in range(world.width - 1):
            for y in range(world.height - 1):
                # search around cell for a direction
                path = self.findQuickPath([x, y], world)
                if path:
                    tx, ty = path
                    flowDir = [tx - x, ty - y]
                    key = 0
                    for direction in DIR_NEIGHBORS_CENTER:
                        if direction == flowDir:
                            waterPath[x, y] = key
                        key += 1

    def findQuickPath(self, river, world):
        # Water flows based on cost, seeking the highest elevation difference
        # highest positive number is the path of least resistance (lowest point)
        # Cost
        # *** 1,0 ***
        # 0,1 *** 2,1
        # *** 1,2 ***
        x, y = river
        newPath = []
        lowestElevation = world.elevation['data'][y][x]
        # lowestDirection = [0, 0]

        for dx, dy in DIR_NEIGHBORS:
            tempDir = [x + dx, y + dy]
            tx, ty = tempDir

            if not self.wrap and world.contains(tempDir):
                continue

            tx, ty = overflow(tx, world.width), overflow(ty, world.height)

            elevation = world.elevation['data'][ty][tx]

            # print river, direction, tempDir, elevation, direction[0], direction[1]

            if elevation < lowestElevation:
                if world.contains(tempDir):
                    #print "Lower OOB:",tempDir, "Corrected:", tx, ty
                    pass
                lowestElevation = elevation
                newPath = [tx,ty]

        # print newPath, lowestDirection, elevation
        # sys.exit()

        return newPath
