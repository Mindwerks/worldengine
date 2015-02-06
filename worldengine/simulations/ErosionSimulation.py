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

def inCircle(radius, center_x, center_y, x, y):
    squareDist = ( (center_x - x) ** 2 + (center_y - y) ** 2 )
    return squareDist <= radius ** 2

class ErosionSimulation(object):

    def __init__(self):
        self.wrap = True

    def is_applicable(self, world):
        return world.has_precipitations()

    def execute(self, world, seed):
        waterFlow = numpy.zeros((world.width, world.height))
        waterPath = numpy.zeros((world.width, world.height), dtype=int)
        self.findWaterFlow(world, waterPath)
        riverSources = self.riverSources(world, waterFlow, waterPath)

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

            if not self.wrap and not world.contains(tempDir):
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

    def riverSources(self, world, waterFlow, waterPath):
        '''Find places on map where sources of river can be found'''
        riverSourceList = []
        # Version 2, with rainfall
        #  Using the wind and rainfall data, create river 'seeds' by
        #     flowing rainfall along paths until a 'flow' threshold is reached
        #     and we have a beginning of a river... trickle->stream->river->sea

        # step one: Using flow direction, follow the path for each cell
        #     adding the previous cell's flow to the current cell's flow.
        # step two: We loop through the water flow map looking for cells
        #     above the water flow threshold. These are our river sources and
        #     we mark them as rivers. While looking, the cells with no
        #     out-going flow, above water flow threshold and are still
        #     above sea level are marked as 'sources'.
        for x in range(0, world.width - 1):
            for y in range(0, world.height - 1):
                rainFall = world.precipitation['data'][y][x]
                waterFlow[x, y] = rainFall

                if waterPath[x, y] == 0:
                    continue  # ignore cells without flow direction
                cx, cy = x, y  # begin with starting location
                neighbourSeedFound = False
                while not neighbourSeedFound:  # follow flow path to where it may lead

                    # have we found a seed?
                    if world.is_mountain((cx, cy)) and waterFlow[cx, cy] >= 10.0:

                        # try not to create seeds around other seeds
                        for seed in riverSourceList:
                            sx, sy = seed
                            if inCircle(9, cx, cy, sx, sy):
                                neighbourSeedFound = True
                        if neighbourSeedFound:
                            break  # we do not want seeds for neighbors

                        riverSourceList.append([cx, cy])  # river seed
                        # self.riverMap[cx,cy] = self.waterFlow[cx,cy] #temp: mark it on map to see 'seed'
                        break

                    # no path means dead end...
                    if waterPath[cx, cy] == 0:
                        break  # break out of loop

                    # follow path, add water flow from previous cell
                    dx, dy = DIR_NEIGHBORS_CENTER[waterPath[cx, cy]]
                    nx, ny = cx + dx, cy + dy  # calculate next cell
                    waterFlow[nx, ny] += rainFall
                    cx, cy = nx, ny  # set current cell to next cell
        return riverSourceList
