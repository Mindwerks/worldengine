import math
import numpy
import worldengine.astar

# Direction
NORTH = [0, -1]
NORTH_EAST = [1, -1]
EAST = [1, 0]
SOUTH_EAST = [1, 1]
SOUTH = [0, 1]
SOUTH_WEST = [-1, 1]
WEST = [-1, 0]
NORTH_WEST = [-1, -1]
CENTER = [0, 0]

DIR_NEIGHBORS = [NORTH, EAST, SOUTH, WEST]
DIR_NEIGHBORS_CENTER = [CENTER, NORTH, EAST, SOUTH, WEST]

RIVER_TH = 0.02


def overflow(value, max_value):
    return value % max_value


def in_circle(radius, center_x, center_y, x, y):
    square_dist = ((center_x - x) ** 2 + (center_y - y) ** 2)
    return square_dist <= radius ** 2


class ErosionSimulation(object):
    def __init__(self):
        self.wrap = True

    def is_applicable(self, world):
        return world.has_precipitations()

    def execute(self, world, seed):
        water_flow = numpy.zeros((world.height, world.width))
        water_path = numpy.zeros((world.height, world.width), dtype=int)
        river_list = []
        lake_list = []
        river_map = numpy.zeros((world.height, world.width))
        lake_map = numpy.zeros((world.height, world.width))

        # step one: water flow per cell based on rainfall
        self.find_water_flow(world, water_path)

        # step two: find river sources (seeds)
        river_sources = self.river_sources(world, water_flow, water_path)

        # step three: for each source, find a path to sea
        for source in river_sources:
            river = self.river_flow(source, world, river_list, lake_list)
            if len(river) > 0:
                river_list.append(river)
                self.cleanUpFlow(river, world)
                rx, ry = river[-1]  # find last cell in river
                if not world.ocean[ry, rx]:
                    lake_list.append(river[-1])  # river flowed into a lake

        # step four: simulate erosion and updating river map
        for river in river_list:
            self.river_erosion(river, world)
            self.rivermap_update(river, water_flow, river_map,
                                 world.precipitation['data'])

        # step five: rivers with no paths to sea form lakes
        for lake in lake_list:
            # print "Found lake at:",lake
            lx, ly = lake
            lake_map[ly, lx] = 0.1  # TODO: make this based on rainfall/flow

        world.set_rivermap(river_map)
        world.set_lakemap(lake_map)

    def find_water_flow(self, world, water_path):
        """Find the flow direction for each cell in heightmap"""

        # iterate through each cell
        for x in range(world.width - 1):
            for y in range(world.height - 1):
                # search around cell for a direction
                path = self.find_quick_path([x, y], world)
                if path:
                    tx, ty = path
                    flow_dir = [tx - x, ty - y]
                    key = 0
                    for direction in DIR_NEIGHBORS_CENTER:
                        if direction == flow_dir:
                            water_path[y, x] = key
                        key += 1

    def find_quick_path(self, river, world):
        # Water flows based on cost, seeking the highest elevation difference
        # highest positive number is the path of least resistance
        # (lowest point)
        # Cost
        # *** 1,0 ***
        # 0,1 *** 2,1
        # *** 1,2 ***
        x, y = river
        new_path = []
        lowest_elevation = world.elevation['data'][y, x]
        # lowestDirection = [0, 0]

        for dx, dy in DIR_NEIGHBORS:
            temp_dir = [x + dx, y + dy]
            tx, ty = temp_dir

            if not self.wrap and not world.contains(temp_dir):
                continue

            tx, ty = overflow(tx, world.width), overflow(ty, world.height)

            elevation = world.elevation['data'][ty, tx]

            if elevation < lowest_elevation:
                if world.contains(temp_dir):
                    pass
                lowest_elevation = elevation
                new_path = [tx, ty]

        return new_path

    @staticmethod
    def river_sources(world, water_flow, water_path):
        """Find places on map where sources of river can be found"""
        river_source_list = []

        # Using the wind and rainfall data, create river 'seeds' by
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
                rain_fall = world.precipitation['data'][y, x]
                water_flow[y, x] = rain_fall

                if water_path[y, x] == 0:
                    continue  # ignore cells without flow direction
                cx, cy = x, y  # begin with starting location
                neighbour_seed_found = False
                # follow flow path to where it may lead
                while not neighbour_seed_found:

                    # have we found a seed?
                    if world.is_mountain((cx, cy)) and \
                            water_flow[cy, cx] >= RIVER_TH:

                        # try not to create seeds around other seeds
                        for seed in river_source_list:
                            sx, sy = seed
                            if in_circle(9, cx, cy, sx, sy):
                                neighbour_seed_found = True
                        if neighbour_seed_found:
                            break  # we do not want seeds for neighbors

                        river_source_list.append([cx, cy])  # river seed
                        break

                    # no path means dead end...
                    if water_path[cy, cx] == 0:
                        break  # break out of loop

                    # follow path, add water flow from previous cell
                    dx, dy = DIR_NEIGHBORS_CENTER[water_path[cy, cx]]
                    nx, ny = cx + dx, cy + dy  # calculate next cell
                    water_flow[ny, nx] += rain_fall
                    cx, cy = nx, ny  # set current cell to next cell
        return river_source_list

    def river_flow(self, source, world, river_list, lake_list):
        """simulate fluid dynamics by using starting point and flowing to the
        lowest available point"""
        current_location = source
        path = [source]

        # start the flow
        while True:
            x, y = current_location

            # is there a river nearby, flow into it
            for dx, dy in DIR_NEIGHBORS:
                ax, ay = x + dx, y + dy
                if self.wrap:
                    ax, ay = overflow(ax, world.width), overflow(ay,
                                                                 world.height)

                for river in river_list:
                    if [ax, ay] in river:
                        merge = False
                        for rx, ry in river:
                            if [ax, ay] == [rx, ry]:
                                merge = True
                                path.append([rx, ry])
                            elif merge:
                                path.append([rx, ry])
                        return path  # skip the rest, return path

            # found a sea?
            if world.ocean[y, x]:
                break

            # find our immediate lowest elevation and flow there
            quick_section = self.find_quick_path(current_location, world)

            if quick_section:
                path.append(quick_section)
                current_location = quick_section
                continue  # stop here and enter back into loop

            is_wrapped, lower_elevation = self.findLowerElevation(
                current_location, world)
            if lower_elevation and not is_wrapped:
                lower_path = worldengine.astar.PathFinder().find(
                    world.elevation['data'], current_location, lower_elevation)
                if lower_path:
                    path += lower_path
                    current_location = path[-1]
                else:
                    break
            elif lower_elevation and is_wrapped:
                # TODO: make this more natural
                max_radius = 40

                cx, cy = current_location
                lx, ly = lower_elevation

                if x < 0 or y < 0 or x > world.width or y > world.height:
                    raise Exception(
                        "BUG: fix me... we shouldn't be here: %s %s" % (
                            current_location, lower_elevation))

                if not in_circle(max_radius, cx, cy, lx, cy):
                    # are we wrapping on x axis?
                    if cx - lx < 0:
                        lx = 0  # move to left edge
                        nx = world.width - 1  # next step is wrapped around
                    else:
                        lx = world.width - 1  # move to right edge
                        nx = 0  # next step is wrapped around
                    ly = ny = int((cy + ly) / 2)  # move halfway
                elif not in_circle(max_radius, cx, cy, cx, ly):
                    # are we wrapping on y axis?
                    if cy - ly < 0:
                        ly = 0  # move to top edge
                        ny = world.height - 1  # next step is wrapped around
                    else:
                        ly = world.height - 1  # move to bottom edge
                        ny = 0  # next step is wrapped around
                    lx = nx = int((cx + lx) / 2)  # move halfway
                else:
                    raise Exception(
                        "BUG: fix me... we are not in circle: %s %s" % (
                            current_location, lower_elevation))

                # find our way to the edge
                edge_path = worldengine.astar.PathFinder().find(
                    world.elevation['data'], [cx, cy], [lx, ly])
                if not edge_path:
                    # can't find another other path, make it a lake
                    lake_list.append(current_location)
                    break
                path += edge_path  # add our newly found path
                path.append([nx, ny])  # finally add our overflow to other side
                current_location = path[-1]

                # find our way to lowest position original found
                lower_path = worldengine.astar.PathFinder().find(
                    world.elevation['data'], current_location, lower_elevation)
                path += lower_path
                current_location = path[-1]

            else:  # can't find any other path, make it a lake
                lake_list.append(current_location)
                break  # end of river

            if not world.contains(current_location):
                print("Why are we here:", current_location)

        return path

    def cleanUpFlow(self, river, world):
        '''Validate that for each point in river is equal to or lower than the
        last'''
        celevation = 1.0
        for r in river:
            rx, ry = r
            relevation = world.elevation['data'][ry, rx]
            if relevation <= celevation:
                celevation = relevation
            elif relevation > celevation:
                world.elevation['data'][ry, rx] = celevation
        return river

    def findLowerElevation(self, source, world):
        '''Try to find a lower elevation with in a range of an increasing
        circle's radius and try to find the best path and return it'''
        x, y = source
        currentRadius = 1
        maxRadius = 40
        lowestElevation = world.elevation['data'][y, x]
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
                    if not in_circle(currentRadius, x, y, rx, ry):
                        continue

                    rx, ry = overflow(rx, world.width), overflow(ry,
                                                                 world.height)

                    # if utilities.outOfBounds([x+cx, y+cy], self.size):
                    #                        print "Fixed:",x ,y,  rx, ry

                    elevation = world.elevation['data'][ry, rx]
                    # have we found a lower elevation?
                    if elevation < lowestElevation:
                        lowestElevation = elevation
                        destination = [rx, ry]
                        notFound = False
                        if not world.contains((x + cx, y + cy)):
                            wrapped.append(destination)

            currentRadius += 1

        if destination in wrapped:
            isWrapped = True
        # print "Wrapped lower elevation found:", rx, ry, "!"
        return isWrapped, destination

    def river_erosion(self, river, world):
        """ Simulate erosion in heightmap based on river path.
            * current location must be equal to or less than previous location
            * riverbed is carved out by % of volume/flow
            * sides of river are also eroded to slope into riverbed.
        """

        # erosion around river, create river valley
        for r in river:
            rx, ry = r
            radius = 2
            for x in range(rx - radius, rx + radius):
                for y in range(ry - radius, ry + radius):
                    if not self.wrap and not world.contains(
                            (x, y)):  # ignore edges of map
                        continue
                    x, y = overflow(x, world.width), overflow(y, world.height)
                    curve = 1.0
                    if [x, y] == [0, 0]:  # ignore center
                        continue
                    if [x, y] in river:  # ignore river itself
                        continue
                    if world.elevation['data'][y, x] <= \
                            world.elevation['data'][ry, 
                                rx]:  # ignore areas lower than river itself
                        continue
                    if not in_circle(radius, rx, ry, x,
                                     y):  # ignore things outside a circle
                        continue

                    adx, ady = math.fabs(rx - x), math.fabs(ry - y)
                    if adx == 1 or ady == 1:
                        curve = 0.2
                    elif adx == 2 or ady == 2:
                        curve = 0.05

                    diff = world.elevation['data'][ry, rx] - \
                        world.elevation['data'][y, x]
                    newElevation = world.elevation['data'][y, x] + (
                        diff * curve)
                    if newElevation <= world.elevation['data'][ry, rx]:
                        print('newElevation is <= than river, fix me...')
                        newElevation = world.elevation['data'][r, x]
                    world.elevation['data'][y, x] = newElevation
        return

    def rivermap_update(self, river, water_flow, rivermap, precipitations):
        """Update the rivermap with the rainfall that is to become
        the waterflow"""

        isSeed = True
        px, py = (0, 0)
        for x, y in river:
            if isSeed:
                rivermap[y, x] = water_flow[y, x]
                isSeed = False
            else:
                rivermap[y, x] = precipitations[y, x] + rivermap[py, px]
            px, py = x, y
