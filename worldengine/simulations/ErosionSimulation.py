from worldengine.simulations.basic import *
import math
import numpy
import lands.aStar

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
        riverList = []
        lakeList = []

        # step one: water flow per cell based on rainfall
        self.findWaterFlow(world, waterPath)

        # step two: find river sources (seeds)
        riverSources = self.riverSources(world, waterFlow, waterPath)

        # step three: for each source, find a path to sea
        for source in riverSources:
            river = self.riverFlow(source, world, riverList, lakeList)
            if len(river) > 0:
                riverList.append(river)
                self.cleanUpFlow(river, world)
                rx, ry = river[-1]  # find last cell in river
                if not world.is_ocean((rx, ry)):
                    lakeList.append(river[-1])  # river flowed into a lake

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

    def riverFlow(self, source, world, riverList, lakeList):
        '''simulate fluid dynamics by using starting point and flowing to the
        lowest available point'''
        currentLocation = source
        path = [source]

        # start the flow
        while True:
            x, y = currentLocation
            lowerElevation = None
            quickSection = None
            isWrapped = False

            for dx, dy in DIR_NEIGHBORS:  # is there a river nearby, flow into it
                ax, ay = x + dx, y + dy
                if self.wrap:
                    ax, ay = overflow(ax, world.width), overflow(ay, world.height)

                for river in riverList:
                    if [ax, ay] in river:
                        #print "Found another river at:", x, y, " -> ", ax, ay, " Thus, using that river's path."
                        merge = False
                        for rx, ry in river:
                            if [ax, ay] == [rx, ry]:
                                merge = True
                                path.append([rx, ry])
                            elif merge == True:
                                path.append([rx, ry])
                        return path  # skip the rest, return path

            # found a sea?
            #print "Flowing to...",x,y
            if world.is_ocean((x,y)):
                break

            # find our immediate lowest elevation and flow there
            quickSection = self.findQuickPath(currentLocation, world)

            if quickSection:
                path.append(quickSection)
                currentLocation = quickSection
                continue # stop here and enter back into loop

            isWrapped, lowerElevation = self.findLowerElevation(currentLocation, world)
            if lowerElevation and not isWrapped:
                lowerPath = None
                lowerPath = aStar.pathFinder().find(world.elevation['data'], currentLocation, lowerElevation)
                if lowerPath:
                    path += lowerPath
                    currentLocation = path[-1]
                else:
                    break
            elif lowerElevation and isWrapped:
                #TODO: make this more natural
                maxRadius = 40
                wrappedX = wrappedY = False
#                print 'Found a lower elevation on wrapped path, searching path!'
#                print 'We go from',currentLocation,'to',lowerElevation
                cx,cy = currentLocation
                lx,ly = lowerElevation
                nx,ny = lowerElevation

                if (x < 0 or y < 0 or x > world.width or y > world.height):
                    print("BUG: fix me... we shouldn't be here:", currentLocation, lowerElevation)
                    break

                if not inCircle(maxRadius, cx, cy, lx, cy):
                    # are we wrapping on x axis?
                    #print "We found wrapping along x-axis"
                    if cx-lx < 0:
                        lx = 0 # move to left edge
                        nx = world.width-1 # next step is wrapped around
                    else:
                        lx = world.width-1 # move to right edge
                        nx = 0 # next step is wrapped around
                    ly = ny = int( (cy+ly)/2 ) # move halfway
                elif not inCircle(maxRadius, cx, cy, cx, ly):
                    # are we wrapping on y axis?
#                    print "We found wrapping along y-axis"
                    if cy-ly < 0:
                        ly = 0 # move to top edge
                        ny = world.height-1 # next step is wrapped around
                    else:
                        ly = world.height-1 # move to bottom edge
                        ny = 0 # next step is wrapped around
                    lx = nx = int( (cx+lx)/2 ) # move halfway
                else:
#                    print "BUG: fix me... we are not in circle:", currentLocation, lowerElevation
                    break

                # find our way to the edge
                edgePath = None
                edgePath = aStar.pathFinder().find(world.elevation['data'], [cx,cy], [lx,ly])
                if not edgePath:
#                    print "We've reached the end of this river, we cannot get through."
                    # can't find another other path, make it a lake
                    lakeList.append(currentLocation)
                    break
                path += edgePath # add our newly found path
                path.append([nx,ny]) # finally add our overflow to other side
                currentLocation = path[-1]
#                print "Path found from ", [cx,cy], 'to', [lx,ly], 'via:'
#                print edgePath
#                print "We then wrap on: ", [nx, ny]

                # find our way to lowest position original found
                lowerPath = aStar.pathFinder().find(world.elevation['data'], currentLocation, lowerElevation)
                path += lowerPath
                currentLocation = path[-1]
#                print "We then go to our destination: ", lowerElevation
#                print lowerPath
#                print " "
#                print "Full path begin and end ", path[0], path[-1]
                hx,hy = path[0]
                hlx,hly = path[-1]
#                print "Elevations: ", self.heightmap[hx,hy], self.heightmap[hlx,hly]
#                print "Erosion: ", self.erosionMap[hx,hy], self.erosionMap[hlx,hly]
#                print " "
                #break
            else: # can't find any other path, make it a lake
                lakeList.append(currentLocation)
                break # end of river

            if not world.contains(currentLocation):
                print("Why are we here:",currentLocation)

        return path

    def cleanUpFlow(self, river, world):
        '''Validate that for each point in river is equal to or lower than the
        last'''
        celevation = 1.0
        for r in river:
            rx, ry = r
            relevation = world.elevation['data'][ry][rx]
            if relevation <= celevation:
                celevation = relevation
            elif relevation > celevation:
                world.elevation['data'][ry][rx] = celevation
        return river

    def findLowerElevation(self, source, world):
        '''Try to find a lower elevation with in a range of an increasing
        circle's radius and try to find the best path and return it'''
        x, y = source
        currentRadius = 1
        maxRadius = 40
        lowestElevation = world.elevation['data'][y][x]
        destination = []
        notFound = True
        isWrapped = False
        wrapped = []

        while notFound and currentRadius <= maxRadius:
            for cx in range(-currentRadius, currentRadius + 1):
                for cy in range(-currentRadius, currentRadius + 1):
                    rx, ry = x + cx, y + cy

                    # are we within bounds?
                    if not self.wrap and not world.contains((rx, ry)):
                        continue

                    # are we within a circle?
                    if not inCircle(currentRadius, x, y, rx, ry):
                        continue

                    rx, ry = overflow(rx, world.width), overflow(ry, world.height)

#                    if utilities.outOfBounds([x+cx, y+cy], self.size):
#                        print "Fixed:",x ,y,  rx, ry

                    elevation = world.elevation['data'][ry][rx]
                    if elevation < lowestElevation: # have we found a lower elevation?
                        lowestElevation = elevation
                        destination = [rx, ry]
                        notFound = False
                        if not world.contains((x+cx, y+cy)):
                            wrapped.append(destination)

            currentRadius += 1

        if destination in wrapped:
            isWrapped = True
#            print "Wrapped lower elevation found:", rx, ry, "!"
        return isWrapped, destination