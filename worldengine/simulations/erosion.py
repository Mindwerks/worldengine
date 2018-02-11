import math
import numpy
from worldengine import astar

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


def gradient_map(shape,elevation):
    """calculate the gradient map"""#Find the flow direction for each cell in heightmap"""
    
    #this is a problem that has been solved to death. there probably
    #is some code out there that can do this better.
    
    height,width=shape
    
    gradient_map=numpy.zeros(shape)
    
    # iterate through each cell
    
    for x in range(width - 1):
        for y in range(height - 1):
            # search around cell for a direction
            
            path = find_quick_path(x, y, elevation)
            
            if path:
                tx, ty = path
                flow_dir = [tx - x, ty - y]
                key = 0
                for direction in DIR_NEIGHBORS_CENTER:
                    if direction == flow_dir:
                        gradient_map[y, x] = key
                    key += 1
                    
    return gradient_map



def river_sources(elevation,precipitation,mountain_th):
    """Find places on map where sources of river can be found"""
    river_source_list = []
    
    shape=precipitation.shape
    height,width=shape
    water_flow = numpy.zeros(shape)
    water_path = numpy.zeros(shape, dtype=int)
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
    for y in range(0, height - 1):
        for x in range(0, width - 1):
            rain_fall = precipitation[y, x]#
            water_flow[y, x] = rain_fall

            if water_path[y, x] == 0:
                continue  # ignore cells without flow direction
            cx, cy = x, y  # begin with starting location
            neighbour_seed_found = False
            # follow flow path to where it may lead
            while not neighbour_seed_found:

                # have we found a seed?
                #world.is_mountain((cx, cy))
                if elevation[cx,cy] > mountain_th and water_flow[cy, cx] >= RIVER_TH:

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
    return river_source_list,water_flow,water_path


def erosion_sim(elevation,precipitation,ocean,mountain_th):
    #hmmm I broke this somewhere...
    
    shape=elevation.shape
    
    river_list = []
    lake_list = []
    river_map = numpy.zeros(shape)
    lake_map = numpy.zeros(shape)

    # step one: water flow per cell based on rainfall
    water_map=gradient_map(shape,elevation)
    gradient=water_map

    # step two: find river sources (seeds)
    river_sources_list,water_flow,water_path = river_sources(elevation,precipitation,mountain_th)
    
    # step three: for each source, find a path to sea
    for source in river_sources_list:
        river = river_flow(source, world, river_list, lake_list)
        if len(river) > 0:
            river_list.append(river)
            elevation=cleanUpFlow(river, elevation)
            rx, ry = river[-1]  # find last cell in river
            if not world.is_ocean((rx, ry)):
                lake_list.append(river[-1])  # river flowed into a lake

    # step four: simulate erosion and updating river map
    for river in river_list:
        river_erosion(river, world)
        rivermap_update(river, water_flow, river_map, precipitation)

    # step five: rivers with no paths to sea form lakes
    for lake in lake_list:
        # print "Found lake at:",lake
        lx, ly = lake
        lake_map[ly, lx] = 0.1  # TODO: make this based on rainfall/flow
    return river_map,lake_map
    

def find_quick_path(x,y, elevation):
    
    # Water flows based on cost, seeking the highest elevation difference
    # highest positive number is the path of least resistance
    # (lowest point)
    # Cost
    # *** 1,0 ***
    # 0,1 *** 2,1
    # *** 1,2 ***
    
    new_path = []
    height,width=elevation.shape
    lowest_elevation = elevation[y,x]
    # lowestDirection = [0, 0]

    for dx, dy in DIR_NEIGHBORS:
        temp_dir = [x + dx, y + dy]
        tx, ty = temp_dir
        
        if not (0 <= temp_dir[0] < width and 0 <= temp_dir[1] < height):
        #if not self.wrap and not world.contains(temp_dir):
            continue

        tx, ty = overflow(tx, width), overflow(ty, height)

        el_i = elevation[ty, tx]

        if el_i < lowest_elevation:
            
            if 0 <= temp_dir[0] < width and 0 <= temp_dir[1] < height:

                pass
                
            lowest_elevation = el_i
            new_path = [tx, ty]

    return new_path

def river_flow(source, elevation, river_list, lake_list):
    """simulate fluid dynamics by using starting point and flowing to the
    lowest available point"""
    current_location = source
    path = [source]
    shape=elevation.shape
    height,width=elevation.shape
    # start the flow
    while True:
        x, y = current_location

        # is there a river nearby, flow into it
        for dx, dy in DIR_NEIGHBORS:
            ax, ay = x + dx, y + dy
            if True:#elf.wrap:
                ax, ay = overflow(ax, shape[1]), overflow(ay, shape[0])

            for river in river_list:
                if [ax, ay] in river:
                    merge = False
                    for rx, ry in river:
                        if [ax, ay] == [rx, ry]:
                            merge = True
                            path.append([rx, ry])
                        elif merge:
                            path.append([rx, ry])
                    #what. this is 100% broken.
                    return path  # skip the rest, return path

        # found a sea?
        if world.is_ocean((x, y)):
            break

        # find our immediate lowest elevation and flow there
        quick_section = find_quick_path(x,y,elevation)##current_location, world)

        if quick_section:
            path.append(quick_section)
            current_location = quick_section
            continue  # stop here and enter back into loop

        is_wrapped, lower_elevation = self.findLowerElevation(current_location, elevation)
        if lower_elevation and not is_wrapped:
            lower_path = astar.PathFinder().find(
                elevation, current_location, lower_elevation)
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

            if x < 0 or y < 0 or x > width or y > height:
                raise Exception(
                    "BUG: fix me... we shouldn't be here: %s %s" % (
                        current_location, lower_elevation))

            if not in_circle(max_radius, cx, cy, lx, cy):
                # are we wrapping on x axis?
                if cx - lx < 0:
                    lx = 0  # move to left edge
                    nx = width - 1  # next step is wrapped around
                else:
                    lx = width - 1  # move to right edge
                    nx = 0  # next step is wrapped around
                ly = ny = int((cy + ly) / 2)  # move halfway
            elif not in_circle(max_radius, cx, cy, cx, ly):
                # are we wrapping on y axis?
                if cy - ly < 0:
                    ly = 0  # move to top edge
                    ny = height - 1  # next step is wrapped around
                else:
                    ly = height - 1  # move to bottom edge
                    ny = 0  # next step is wrapped around
                lx = nx = int((cx + lx) / 2)  # move halfway
            else:
                raise Exception(
                    "BUG: fix me... we are not in circle: %s %s" % (
                        current_location, lower_elevation))

            # find our way to the edge
            edge_path = astar.PathFinder().find(
            elevation, [cx, cy], [lx, ly])
            if not edge_path:
                # can't find another other path, make it a lake
                lake_list.append(current_location)
                break
            path += edge_path  # add our newly found path
            path.append([nx, ny])  # finally add our overflow to other side
            current_location = path[-1]

            # find our way to lowest position original found
            lower_path = astar.PathFinder().find(
                elevation, current_location, lower_elevation)
            path += lower_path
            current_location = path[-1]

        else:  # can't find any other path, make it a lake
            lake_list.append(current_location)
            break  # end of river
        pos=current_location
        if not (0 <= pos[0] < width and 0 <= pos[1] < height):
        #if not world.contains(current_location):
            print("Why are we here:", current_location)
            #good question though.

    return path

def cleanUpFlow(river, elevation):
    '''Validate that for each point in river is equal to or lower than the
    last'''
    celevation = 1.0
    for r in river:
        rx, ry = r
        relevation = elevation[ry, rx]
        if relevation <= celevation:
            celevation = relevation
        elif relevation > celevation:
            elevation[ry, rx] = celevation
    return elevation
    
def findLowerElevation(source, elevation_map):
    '''Try to find a lower elevation with in a range of an increasing
    circle's radius and try to find the best path and return it'''
    x, y = source
    currentRadius = 1
    maxRadius = 40
    lowestElevation = elevation_map[y,x]# world.layers['elevation'].data[y, x]
    destination = []
    notFound = True
    isWrapped = False
    wrapped = []
    shape=elevation_map.shape
    height,width=shape
    while notFound and currentRadius <= maxRadius:
        for cx in range(-currentRadius, currentRadius + 1):
            for cy in range(-currentRadius, currentRadius + 1):
                rx, ry = x + cx, y + cy

                # are we within bounds?
                pos=(rx, ry)
                conts=(0 <= pos[0] < width and 0 <= pos[1] < height)
                if not self.wrap and not conts:
                    continue

                # are we within a circle?
                if not in_circle(currentRadius, x, y, rx, ry):
                    continue

                rx, ry = overflow(rx,width), overflow(ry,height)

                # if utilities.outOfBounds([x+cx, y+cy], self.size):
                #                        print "Fixed:",x ,y,  rx, ry

                elevation = elevation_map[ry,rx]# world.layers['elevation'].data[ry, rx]
                # have we found a lower elevation?
                if elevation < lowestElevation:
                    lowestElevation = elevation
                    destination = [rx, ry]
                    notFound = False
                    #0 <= temp_dir[0] < width and 0 <= temp_dir[1] < height:
                    pos=(x + cx, y + cy)
                    if not (0 <= pos[0] < width and 0 <= pos[1] < height):
                        
 #world.contains((x + cx, y + cy)):
                        wrapped.append(destination)

        currentRadius += 1

    if destination in wrapped:
        isWrapped = True
    # print "Wrapped lower elevation found:", rx, ry, "!"
    return isWrapped, destination

def river_erosion( river, world):
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
                if world.layers['elevation'].data[y, x] <= world.layers['elevation'].data[ry, rx]:
                    # ignore areas lower than river itself
                    continue
                if not in_circle(radius, rx, ry, x,
                                 y):  # ignore things outside a circle
                    continue

                adx, ady = math.fabs(rx - x), math.fabs(ry - y)
                if adx == 1 or ady == 1:
                    curve = 0.2
                elif adx == 2 or ady == 2:
                    curve = 0.05

                diff = world.layers['elevation'].data[ry, rx] - world.layers['elevation'].data[y, x]
                newElevation = world.layers['elevation'].data[y, x] + (
                    diff * curve)
                if newElevation <= world.layers['elevation'].data[ry, rx]:
                    print('newElevation is <= than river, fix me...')
                    newElevation = world.layers['elevation'].data[r, x]
                world.layers['elevation'].data[y, x] = newElevation
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
