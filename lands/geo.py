__author__ = 'Federico Tomassetti'

import time
from noise import snoise2
from lands.world import *
from lands.simulations.WatermapSimulation import *
from lands.simulations.IrrigationSimulation import *
from lands.simulations.HumiditySimulation import *
from lands.simulations.TemperatureSimulation import *
from lands.simulations.PermeabilitySimulation import *
from lands.simulations.ErosionSimulation import *
from lands.simulations.BiomeSimulation import *
from lands.simulations.basic import *
from lands.common import *

import sys
if sys.version_info > (2,):
    xrange = range


def center_land(world):
    """Translate the map horizontally and vertically to put as much ocean as possible at the borders.
       It operates on elevation and plates map"""
    miny = None
    ymin = None
    minx = None
    xmin = None

    for y in xrange(world.height):
        sumy = 0
        for x in xrange(world.width):
            sumy += world.elevation['data'][y][x]
        if miny is None or sumy < miny:
            miny = sumy
            ymin = y
    if get_verbose():
        print("geo.center_land: height complete");

    for x in xrange(world.width):
        sumx = 0
        for y in xrange(world.height):
            sumx += world.elevation['data'][y][x]
        if minx is None or sumx < minx:
            minx = sumx
            xmin = x
    if get_verbose():
        print("geo.center_land: width complete");

    new_elevation_data = []
    new_plates         = []
    for y in xrange(world.height):
        new_elevation_data.append([])
        new_plates.append([])
        srcy = (ymin + y) % world.height
        for x in xrange(world.width):
            srcx = (xmin + x) % world.width
            new_elevation_data[y].append( world.elevation['data'][srcy][srcx] )
            new_plates[y].append( world.plates[srcy][srcx] )
    world.elevation['data'] = new_elevation_data
    world.plates = new_plates
    if get_verbose():
        print("geo.center_land: width complete");


def center_elevation_map(elevation, width, height):
    """Translate the map horizontally and vertically to put as much ocean as possible at the borders."""
    # FIXME this is bad because plates are not translated
    miny = None
    ymin = None
    minx = None
    xmin = None

    for y in xrange(height):
        sumy = 0
        for x in xrange(width):
            sumy += elevation[y * width + x]
        if miny is None or sumy < miny:
            miny = sumy
            ymin = y

    for x in xrange(width):
        sumx = 0
        for y in xrange(height):
            sumx += elevation[y * width + x]
        if minx is None or sumx < minx:
            minx = sumx
            xmin = x

    new_elevation = [0] * (width * height)
    for y in xrange(height):
        srcy = (ymin + y) % height
        for x in xrange(width):
            srcx = (xmin + x) % width
            new_elevation[y * width + x] = elevation[srcy * width + srcx]
    elevation = new_elevation

    return elevation


def get_interleave_value(original_map, x, y):
    """x and y can be float value"""
    weight_next_x, base_x = math.modf(x)
    weight_preceding_x = 1.0 - weight_next_x
    weight_next_y, base_y = math.modf(y)
    weight_preceding_y = 1.0 - weight_next_y

    base_x = int(base_x)
    base_y = int(base_y)

    sum = 0.0

    # In case the point is right on the border, the weight
    # of the next point will be zero and we will not access
    # it
    combined_weight = weight_preceding_x * weight_preceding_y
    if combined_weight > 0.0:
        sum += combined_weight * original_map[base_y][base_x]

    combined_weight = weight_preceding_x * weight_next_y
    if combined_weight > 0.0:
        sum += combined_weight * original_map[base_y + 1][base_x]

    combined_weight = weight_next_x * weight_preceding_y
    if combined_weight > 0.0:
        sum += combined_weight * original_map[base_y][base_x + 1]

    combined_weight = weight_next_x * weight_next_y
    if combined_weight > 0.0:
        sum += combined_weight * original_map[base_y + 1][base_x + 1]

    return sum


def scale(original_map, target_width, target_height):
    original_width = len(original_map[0])
    original_height = len(original_map)

    y_factor = float(original_height - 1) / (target_height - 1)
    x_factor = float(original_width - 1) / (target_width - 1)

    scaled_map = [[0 for x in xrange(target_width)] for y in xrange(target_height)]
    for scaled_y in xrange(target_height):
        original_y = y_factor * scaled_y
        for scaled_x in xrange(target_width):
            original_x = x_factor * scaled_x
            scaled_map[scaled_y][scaled_x] = get_interleave_value(original_map, original_x, original_y)

    return scaled_map


def get_interleave_value_in_array(original_map, width, height, x, y):
    """x and y can be float value"""
    weight_next_x, base_x = math.modf(x)
    weight_preceding_x = 1.0 - weight_next_x
    weight_next_y, base_y = math.modf(y)
    weight_preceding_y = 1.0 - weight_next_y

    base_x = int(base_x)
    base_y = int(base_y)

    sum = 0.0

    # In case the point is right on the border, the weight
    # of the next point will be zero and we will not access
    # it
    combined_weight = weight_preceding_x * weight_preceding_y
    if combined_weight > 0.0:
        sum += combined_weight * original_map[base_y * width + base_x]

    combined_weight = weight_preceding_x * weight_next_y
    if combined_weight > 0.0:
        sum += combined_weight * original_map[(base_y + 1) * width + base_x]

    combined_weight = weight_next_x * weight_preceding_y
    if combined_weight > 0.0:
        sum += combined_weight * original_map[(base_y) * width + base_x + 1]

    combined_weight = weight_next_x * weight_next_y
    if combined_weight > 0.0:
        sum += combined_weight * original_map[(base_y + 1) * width + base_x + 1]

    return sum


def scale_map_in_array(original_map, original_width, original_height, target_width, target_height):
    y_factor = float(original_height - 1) / (target_height - 1)
    x_factor = float(original_width - 1) / (target_width - 1)

    scaled_map = [0 for el in xrange(target_width * target_height)]
    for scaled_y in xrange(target_height):
        original_y = y_factor * scaled_y
        for scaled_x in xrange(target_width):
            original_x = x_factor * scaled_x
            scaled_map[scaled_y * target_width + scaled_x] = get_interleave_value_in_array(original_map, original_width,
                                                                                           original_height, original_x,
                                                                                           original_y)

    return scaled_map


def matrix_extremes(matrix):
    min = None
    max = None
    for row in matrix:
        for el in row:
            val = el
            if min is None or val < min:
                min = val
            if max is None or val > max:
                max = val
    return (min, max)


def rescale_value(original, prev_min, prev_max, min, max):
    f = float(original - prev_min) / (prev_max - prev_min)
    return min + ((max - min) * f)


def sea_depth(world, sea_level):
    sea_depth = [[sea_level - world.elevation['data'][y][x] for x in xrange(world.width)] for y in xrange(world.height)]
    for y in xrange(world.height):
        for x in xrange(world.width):
            if world.tiles_around((x, y), radius=1, predicate=world.is_land):
                sea_depth[y][x] = 0
            elif world.tiles_around((x, y), radius=2, predicate=world.is_land):
                sea_depth[y][x] *= 0.3
            elif world.tiles_around((x, y), radius=3, predicate=world.is_land):
                sea_depth[y][x] *= 0.5
            elif world.tiles_around((x, y), radius=4, predicate=world.is_land):
                sea_depth[y][x] *= 0.7
            elif world.tiles_around((x, y), radius=5, predicate=world.is_land):
                sea_depth[y][x] *= 0.9
    antialias(sea_depth, 10)
    min_depth, max_depth = matrix_extremes(sea_depth)
    sea_depth = [[rescale_value(sea_depth[y][x], min_depth, max_depth, 0.0, 1.0) for x in xrange(world.width)] for y in
                 xrange(world.height)]
    return sea_depth


def antialias(elevation, steps):
    width = len(elevation[0])
    height = len(elevation)

    def antialias():
        for y in range(0, height):
            for x in range(0, width):
                antialias_point(x, y)

    def antialias_point(x, y):
        n = 2
        tot = elevation[y][x] * 2
        for dy in range(-1, +2):
            py = y + dy
            if py > 0 and py < height:
                for dx in range(-1, +2):
                    px = x + dx
                    if px > 0 and px < width:
                        n += 1
                        tot += elevation[py][px]
        return tot / n

    for i in range(0, steps):
        antialias()


def around(x, y, width, height):
    ps = []
    for dx in range(-1, 2):
        nx = x + dx
        if nx >= 0 and nx < width:
            for dy in range(-1, 2):
                ny = y + dy
                if ny >= 0 and ny < height and (dx != 0 or dy != 0):
                    ps.append((nx, ny))
    return ps


def fill_ocean(elevation, sea_level):
    width = len(elevation[0])
    height = len(elevation)

    ocean = [[False for x in xrange(width)] for y in xrange(height)]
    to_expand = []
    for x in range(0, width):
        if elevation[0][x] <= sea_level:
            to_expand.append((x, 0))
        if elevation[height -1][x] <= sea_level:
            to_expand.append((x, height - 1))
    for y in range(0, height):
        if elevation[y][0] <= sea_level:
            to_expand.append((0, y))
        if elevation[y][width - 1] <= sea_level:
            to_expand.append((width - 1, y))
    for t in to_expand:
        tx, ty = t
        if not ocean[ty][tx]:
            ocean[ty][tx] = True
            for px, py in around(tx, ty, width, height):
                if not ocean[py][px] and elevation[py][px] <= sea_level:
                    to_expand.append((px, py))

    return ocean


def precipitation(seed, width, height):
    """"Precipitation is a value in [-1,1]"""
    border = width / 4 
    random.seed(seed * 13)
    base = random.randint(0, 4096)
    precipitations = [[0 for x in xrange(width)] for y in xrange(height)]

    from noise import snoise2

    octaves = 6
    freq = 64.0 * octaves

    for y in range(0, height):
        yscaled = float(y) / height
        latitude_factor = 1.0 - (abs(yscaled - 0.5) * 2)
        for x in range(0, width):
            n = snoise2(x / freq, y / freq, octaves, base=base)

            # Added to allow noise pattern to wrap around right and left.
            if x < border: 
                n = (snoise2(x / freq, y / freq, octaves, base=base) * x / border) + (snoise2((x+width) / freq, y / freq, octaves, base=base) * (border-x)/border)

            prec = (latitude_factor + n * 4) / 5.0
            precipitations[y][x] = prec

    return precipitations


def classify(data, thresholds, x, y):
    value = data[y][x]
    for name, level in thresholds:
        if (level is None) or (value < level):
            return name


def elevnoise_on_world(world, seed):
    octaves = 6
    freq = 16.0 * octaves
    for y in range(0, world.height):
        for x in range(0, world.width):
            n = snoise2(x / freq * 2, y / freq * 2, octaves, base=seed)
            world.elevation['data'][y][x] += n


def elevnoise(elevation, seed):
    # FIXME use elevnoise_on_world instead
    width = len(elevation[0])
    height = len(elevation)

    octaves = 6
    freq = 16.0 * octaves
    for y in range(0, height):
        for x in range(0, width):
            n = int(snoise2(x / freq * 2, y / freq * 2, octaves, base=seed))
            elevation[y][x] += n


def place_oceans_at_map_borders_on_world(world):
    """
    Lower the elevation near the border of the map
    """

    OCEAN_BORDER = int(min(30, max(world.width / 5, world.height / 5)))

    def place_ocean(x, y, i):
        world.elevation['data'][y][x] = (world.elevation['data'][y][x] * i) / OCEAN_BORDER

    for x in xrange(world.width):
        for i in range(0, OCEAN_BORDER):
            place_ocean(x, i, i)
            place_ocean(x, world.height - i - 1, i)

    for y in xrange(world.height):
        for i in range(0, OCEAN_BORDER):
            place_ocean(i, y, i)
            place_ocean(world.width - i - 1, y, i)


def place_oceans_at_map_borders(elevation):
    """
    Lower the elevation near the border of the map
    :param elevation:
    :return:
    """
    # FIXME remove and use place_ocenas_at_map_borders_on_world instead
    width = len(elevation[0])
    height = len(elevation)

    OCEAN_BORDER = int(min(30, max(width / 5, height / 5)))

    def place_ocean(x, y, i):
        elevation[y][x] = (elevation[y][x] * i) / OCEAN_BORDER
    
    for x in xrange(width):
        for i in range(0, OCEAN_BORDER):
            place_ocean(x, i, i)
            place_ocean(x, height - i - 1, i)


def initialize_ocean_and_thresholds(world, ocean_level=1.0):
    """
    Calculate the ocean, the sea depth and the elevation thresholds
    :param world: a world having elevation but not thresholds
    :param ocean_level: the elevation representing the ocean level
    :return: nothing, the world will be changed
    """
    e = world.elevation['data']
    ocean = fill_ocean(e, ocean_level)
    hl = find_threshold_f(e, 0.10)
    ml = find_threshold_f(e, 0.03)
    e_th = [('sea', ocean_level), ('plain', hl), ('hill', ml), ('mountain', None)]
    world.set_ocean(ocean)
    world.set_elevation(e, e_th)
    world.sea_depth = sea_depth(world, ocean_level)


def world_gen_precipitation(w, seed):
    start_time = time.time()
    p = precipitation(seed, w.width, w.height)
    p_th = [
        ('low', find_threshold_f(p, 0.75, w.ocean)),
        ('med', find_threshold_f(p, 0.3, w.ocean)),
        ('hig', None)
    ]
    w.set_precipitation(p, p_th)
    elapsed_time = time.time() - start_time
    if get_verbose():
        print("...precipitations calculated. Elapsed time %f  seconds." % elapsed_time)
    return [p, p_th]


def world_gen_from_elevation(w, step):
    if isinstance(step, str):
        step = Step.get_by_name(step)
    e = w.elevation['data']
    ocean = w.ocean
    ml = w.start_mountain_th()
    seed = w.seed

    if not step.include_precipitations:
        return w

    # Precipitation with thresholds
    p, p_th = world_gen_precipitation(w, seed)

    if not step.include_erosion:
        return w
    ErosionSimulation().execute(w, seed)
    if get_verbose():
        print("...erosion calculated")

    WatermapSimulation().execute(w, seed)

    # FIXME: create setters
    IrrigationSimulation().execute(w, seed)
    HumiditySimulation().execute(w, seed)

    TemperatureSimulation().execute(w, seed)
    PermeabilitySimulation().execute(w, seed)



    cm, biome_cm = BiomeSimulation().execute(w, seed)
    for cl in cm.keys():
        count = cm[cl]
        if get_verbose():
            print("%s = %i" % (str(cl), count))

    if get_verbose():
        print('')  # empty line
        print('Biome obtained:')

    for cl in biome_cm.keys():
        count = biome_cm[cl]
        if get_verbose():
            print(" %30s = %7i" % (str(cl), count))

    return w


