from noise import snoise2
from worldengine.world import Step
from worldengine.simulations.basic import find_threshold_f
from worldengine.simulations.hydrology import WatermapSimulation
from worldengine.simulations.irrigation import IrrigationSimulation
from worldengine.simulations.humidity import HumiditySimulation
from worldengine.simulations.temperature import TemperatureSimulation
from worldengine.simulations.permeability import PermeabilitySimulation
from worldengine.simulations.erosion import ErosionSimulation
from worldengine.simulations.precipitation import PrecipitationSimulation
from worldengine.simulations.biome import BiomeSimulation
from worldengine.common import anti_alias, get_verbose
import numpy


# ------------------
# Initial generation
# ------------------

def center_land(world):
    """Translate the map horizontally and vertically to put as much ocean as
       possible at the borders. It operates on elevation and plates map"""

    min_sum_on_y = None
    y_with_min_sum = None
    latshift = 0
    for y in range(world.height):
        sum_on_y = world.elevation['data'][y].sum()
        if min_sum_on_y is None or sum_on_y < min_sum_on_y:
            min_sum_on_y = sum_on_y
            y_with_min_sum = y
    if get_verbose():
        print("geo.center_land: height complete")

    min_sum_on_x = None
    x_with_min_sum = None
    for x in range(world.width):
        sum_on_x = world.elevation['data'].T[x].sum()
        if min_sum_on_x is None or sum_on_x < min_sum_on_x:
            min_sum_on_x = sum_on_x
            x_with_min_sum = x
    if get_verbose():
        print("geo.center_land: width complete")

    new_elevation_data = [] #TODO: this should fully use numpy
    new_plates = []
    for y in range(world.height):
        new_elevation_data.append([])
        new_plates.append([])
        src_y = (y_with_min_sum + y - latshift) % world.height
        for x in range(world.width):
            src_x = (x_with_min_sum + x) % world.width
            new_elevation_data[y].append(world.elevation['data'][src_y, src_x])
            new_plates[y].append(world.plates[src_y][src_x])
    world.elevation['data'] = numpy.array(new_elevation_data)
    world.plates = new_plates
    if get_verbose():
        print("geo.center_land: width complete")


def place_oceans_at_map_borders(world):
    """
    Lower the elevation near the border of the map
    """

    ocean_border = int(min(30, max(world.width / 5, world.height / 5)))

    def place_ocean(x, y, i):
        world.elevation['data'][y, x] = \
            (world.elevation['data'][y, x] * i) / ocean_border

    for x in range(world.width):
        for i in range(ocean_border):
            place_ocean(x, i, i)
            place_ocean(x, world.height - i - 1, i)

    for y in range(world.height):
        for i in range(ocean_border):
            place_ocean(i, y, i)
            place_ocean(world.width - i - 1, y, i)


def add_noise_to_elevation(world, seed):
    octaves = 8
    freq = 16.0 * octaves
    for y in range(world.height):
        for x in range(world.width):
            n = snoise2(x / freq * 2, y / freq * 2, octaves, base=seed)
            world.elevation['data'][y, x] += n


def fill_ocean(elevation, sea_level):#TODO: Make more use of numpy?
    height, width = elevation.shape

    ocean = numpy.zeros(elevation.shape, dtype=bool)
    to_expand = []
    for x in range(width):#handle top and bottom border of the map
        if elevation[0, x] <= sea_level:
            to_expand.append((x, 0))
        if elevation[height - 1, x] <= sea_level:
            to_expand.append((x, height - 1))
    for y in range(height):#handle left- and rightmost border of the map
        if elevation[y, 0] <= sea_level:
            to_expand.append((0, y))
        if elevation[y, width - 1] <= sea_level:
            to_expand.append((width - 1, y))
    for t in to_expand:
        tx, ty = t
        if not ocean[ty, tx]:
            ocean[ty, tx] = True
            for px, py in _around(tx, ty, width, height):
                if not ocean[py, px] and elevation[py, px] <= sea_level:
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
    e_th = [('sea', ocean_level),
            ('plain', hl),
            ('hill', ml),
            ('mountain', None)]
    harmonize_ocean(ocean, e, ocean_level)
    world.set_ocean(ocean)
    world.set_elevation(e, e_th)
    world.sea_depth = sea_depth(world, ocean_level)


def harmonize_ocean(ocean, elevation, ocean_level):
    """
    The goal of this function is to make the ocean floor less noisy.
    The underwater erosion should cause the ocean floor to be more uniform
    """

    shallow_sea = ocean_level * 0.85
    midpoint = shallow_sea / 2.0

    ocean_points = numpy.logical_and(elevation < shallow_sea, ocean)

    shallow_ocean = numpy.logical_and(elevation < midpoint, ocean_points)
    elevation[shallow_ocean] = midpoint - ((midpoint - elevation[shallow_ocean]) / 5.0)

    deep_ocean = numpy.logical_and(elevation > midpoint, ocean_points)
    elevation[deep_ocean] = midpoint + ((elevation[deep_ocean] - midpoint) / 5.0)

# ----
# Misc
# ----

def sea_depth(world, sea_level):
    sea_depth = sea_level - world.elevation['data']
    for y in range(world.height):
        for x in range(world.width):
            if world.tiles_around((x, y), radius=1, predicate=world.is_land):
                sea_depth[y, x] = 0
            elif world.tiles_around((x, y), radius=2, predicate=world.is_land):
                sea_depth[y, x] *= 0.3
            elif world.tiles_around((x, y), radius=3, predicate=world.is_land):
                sea_depth[y, x] *= 0.5
            elif world.tiles_around((x, y), radius=4, predicate=world.is_land):
                sea_depth[y, x] *= 0.7
            elif world.tiles_around((x, y), radius=5, predicate=world.is_land):
                sea_depth[y, x] *= 0.9
    sea_depth = anti_alias(sea_depth, 10)

    min_depth = sea_depth.min()
    max_depth = sea_depth.max()
    sea_depth = (sea_depth - min_depth) / (max_depth - min_depth)
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

    TemperatureSimulation().execute(w, seed)
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
