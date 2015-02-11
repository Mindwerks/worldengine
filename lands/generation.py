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
from lands.simulations.PrecipitationSimulation import *
from lands.simulations.BiomeSimulation import *
from lands.simulations.basic import *
from lands.common import *


# ------------------
# Initial generation
# ------------------

def center_land(world):
    """Translate the map horizontally and vertically to put as much ocean as possible at the borders.
       It operates on elevation and plates map"""
    miny = None
    ymin = None
    minx = None
    xmin = None

    for y in range(world.height):
        sumy = 0
        for x in range(world.width):
            sumy += world.elevation['data'][y][x]
        if miny is None or sumy < miny:
            miny = sumy
            ymin = y
    if get_verbose():
        print("geo.center_land: height complete")

    for x in range(world.width):
        sumx = 0
        for y in range(world.height):
            sumx += world.elevation['data'][y][x]
        if minx is None or sumx < minx:
            minx = sumx
            xmin = x
    if get_verbose():
        print("geo.center_land: width complete")

    new_elevation_data = []
    new_plates         = []
    for y in range(world.height):
        new_elevation_data.append([])
        new_plates.append([])
        srcy = (ymin + y) % world.height
        for x in range(world.width):
            srcx = (xmin + x) % world.width
            new_elevation_data[y].append( world.elevation['data'][srcy][srcx] )
            new_plates[y].append( world.plates[srcy][srcx] )
    world.elevation['data'] = new_elevation_data
    world.plates = new_plates
    if get_verbose():
        print("geo.center_land: width complete")


def place_oceans_at_map_borders(world):
    """
    Lower the elevation near the border of the map
    """

    ocean_border = int(min(30, max(world.width / 5, world.height / 5)))

    def place_ocean(x, y, i):
        world.elevation['data'][y][x] = (world.elevation['data'][y][x] * i) / ocean_border

    for x in range(world.width):
        for i in range(ocean_border):
            place_ocean(x, i, i)
            place_ocean(x, world.height - i - 1, i)

    for y in range(world.height):
        for i in range(ocean_border):
            place_ocean(i, y, i)
            place_ocean(world.width - i - 1, y, i)


def add_noise_to_elevation(world, seed):
    octaves = 6
    freq = 16.0 * octaves
    for y in range(world.height):
        for x in range(world.width):
            n = snoise2(x / freq * 2, y / freq * 2, octaves, base=seed)
            world.elevation['data'][y][x] += n


def fill_ocean(elevation, sea_level):
    width = len(elevation[0])
    height = len(elevation)

    ocean = [[False for x in range(width)] for y in range(height)]
    to_expand = []
    for x in range(width):
        if elevation[0][x] <= sea_level:
            to_expand.append((x, 0))
        if elevation[height -1][x] <= sea_level:
            to_expand.append((x, height - 1))
    for y in range(height):
        if elevation[y][0] <= sea_level:
            to_expand.append((0, y))
        if elevation[y][width - 1] <= sea_level:
            to_expand.append((width - 1, y))
    for t in to_expand:
        tx, ty = t
        if not ocean[ty][tx]:
            ocean[ty][tx] = True
            for px, py in _around(tx, ty, width, height):
                if not ocean[py][px] and elevation[py][px] <= sea_level:
                    to_expand.append((px, py))

    return ocean


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


# ----
# Misc
# ----

def sea_depth(world, sea_level):
    sea_depth = [[sea_level - world.elevation['data'][y][x] for x in range(world.width)] for y in range(world.height)]
    for y in range(world.height):
        for x in range(world.width):
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
    sea_depth = antialias(sea_depth, 10)
    min_depth, max_depth = matrix_min_and_max(sea_depth)
    sea_depth = [[rescale_value(sea_depth[y][x], min_depth, max_depth, 0.0, 1.0) for x in range(world.width)] for y in
                 range(world.height)]
    return sea_depth


def _around(x, y, width, height):
    ps = []
    for dx in range(-1, 2):
        nx = x + dx
        if 0 <= nx < width:
            for dy in range(-1, 2):
                ny = y + dy
                if 0 <= ny < height and (dx != 0 or dy != 0):
                    ps.append((nx, ny))
    return ps


def generate_world(w, step):
    if isinstance(step, str):
        step = Step.get_by_name(step)
    seed = w.seed

    if not step.include_precipitations:
        return w

    # Precipitation with thresholds
    PrecipitationSimulation().execute(w, seed)

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
