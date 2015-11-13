import numpy

from worldengine.drawing_functions import draw_ancientmap, \
    draw_rivers_on_image
from worldengine.image_io import PNGWriter

# -------------
# Helper values
# -------------

### For draw_satellite ###
NOISE_RANGE = 15 # a random value between -NOISE_RANGE and NOISE_RANGE will be added to the rgb of each pixel

# These are arbitrarily-chosen elevation cutoffs for 4 different height levels. 
# Some color modifiers will be applied at each level
HIGH_MOUNTAIN_ELEV = 215
MOUNTAIN_ELEV      = 175
HIGH_HILL_ELEV     = 160
HILL_ELEV          = 145

# These are rgb color values which will be added to the noise, if the elevation is greater than the height specified
# These are not cumulative
HIGH_MOUNTAIN_NOISE_MODIFIER = (10, 6,   10)
MOUNTAIN_NOISE_MODIFIER =      (-4, -12, -4)
HIGH_HILL_NOISE_MODIFIER =     (-3, -10, -3)
HILL_NOISE_MODIFIER =          (-2, -6,  -2)

# This is the base "mountain color". Elevations above this size will have their colors interpolated with this 
# color in order to give a more mountainous appearance
MOUNTAIN_COLOR = (50, 57, 28)

# If a tile is a river or a lake, the color of the tile will change by this amount
RIVER_COLOR_CHANGE = (-12, -12, 4)
LAKE_COLOR_CHANGE = (-12, -12, 10)

# The normalized (0-255) value of an elevation of a tile gets divided by this amount, and added to a tile's color
BASE_ELEVATION_INTENSITY_MODIFIER = 10

# How many tiles to average together when comparing this tile's elevation to the previous tiles.
SAT_SHADOW_SIZE = 5
# How much to multiply the difference in elevation between this tile and the previous tile
# Higher will result in starker contrast between high and low areas.
SAT_SHADOW_DISTANCE_MULTIPLIER = 9

### end values for draw_satellite ###


_biome_colors = {
    'ocean': (23, 94, 145),
    'sea': (23, 94, 145),
    'ice': (255, 255, 255),
    'subpolar dry tundra': (128, 128, 128),
    'subpolar moist tundra': (96, 128, 128),
    'subpolar wet tundra': (64, 128, 128),
    'subpolar rain tundra': (32, 128, 192),
    'polar desert': (192, 192, 192),
    'boreal desert': (160, 160, 128),
    'cool temperate desert': (192, 192, 128),
    'warm temperate desert': (224, 224, 128),
    'subtropical desert': (240, 240, 128),
    'tropical desert': (255, 255, 128),
    'boreal rain forest': (32, 160, 192),
    'cool temperate rain forest': (32, 192, 192),
    'warm temperate rain forest': (32, 224, 192),
    'subtropical rain forest': (32, 240, 176),
    'tropical rain forest': (32, 255, 160),
    'boreal wet forest': (64, 160, 144),
    'cool temperate wet forest': (64, 192, 144),
    'warm temperate wet forest': (64, 224, 144),
    'subtropical wet forest': (64, 240, 144),
    'tropical wet forest': (64, 255, 144),
    'boreal moist forest': (96, 160, 128),
    'cool temperate moist forest': (96, 192, 128),
    'warm temperate moist forest': (96, 224, 128),
    'subtropical moist forest': (96, 240, 128),
    'tropical moist forest': (96, 255, 128),
    'warm temperate dry forest': (128, 224, 128),
    'subtropical dry forest': (128, 240, 128),
    'tropical dry forest': (128, 255, 128),
    'boreal dry scrub': (128, 160, 128),
    'cool temperate desert scrub': (160, 192, 128),
    'warm temperate desert scrub': (192, 224, 128),
    'subtropical desert scrub': (208, 240, 128),
    'tropical desert scrub': (224, 255, 128),
    'cool temperate steppe': (128, 192, 128),
    'warm temperate thorn scrub': (160, 224, 128),
    'subtropical thorn woodland': (176, 240, 128),
    'tropical thorn woodland': (192, 255, 128),
    'tropical very dry forest': (160, 255, 128),
}

# These colors are used when drawing the satellite view map
# The rgb values were hand-picked from an actual high-resolution 
# satellite map of earth. However, many values are either too similar
# to each other or otherwise need to be updated. It is recommended that
# further research go into these values, making sure that each rgb is
# actually picked from a region on earth that has the matching biome
_biome_satellite_colors = {
    'ocean': (23, 94, 145),
    'sea': (23, 94, 145),
    'ice': (255, 255, 255),
    'subpolar dry tundra': (186, 199, 206),
    'subpolar moist tundra': (186, 195, 202),
    'subpolar wet tundra': (186, 195, 204),
    'subpolar rain tundra': (186, 200, 210),
    'polar desert': (182, 195, 201),
    'boreal desert': (132, 146, 143),
    'cool temperate desert': (183, 163, 126),
    'warm temperate desert': (166, 142, 104),
    'subtropical desert': (205, 181, 137),
    'tropical desert': (203, 187, 153),
    'boreal rain forest': (21, 29, 8),
    'cool temperate rain forest': (25, 34, 15),
    'warm temperate rain forest': (19, 28, 7),
    'subtropical rain forest': (48, 60, 24),
    'tropical rain forest': (21, 38, 6),
    'boreal wet forest': (6, 17, 11),
    'cool temperate wet forest': (6, 17, 11),
    'warm temperate wet forest': (44, 48, 19),
    'subtropical wet forest': (23, 36, 10),
    'tropical wet forest': (23, 36, 10),
    'boreal moist forest': (31, 39, 18),
    'cool temperate moist forest': (31, 39, 18),
    'warm temperate moist forest': (36, 42, 19),
    'subtropical moist forest': (23, 31, 10),
    'tropical moist forest': (24, 36, 11),
    'warm temperate dry forest': (52, 51, 30),
    'subtropical dry forest': (53, 56, 30),
    'tropical dry forest': (54, 60, 30),
    'boreal dry scrub': (73, 70, 61),
    'cool temperate desert scrub': (80, 58, 44),
    'warm temperate desert scrub': (92, 81, 49),
    'subtropical desert scrub': (68, 57, 35),
    'tropical desert scrub': (107, 87, 60),
    'cool temperate steppe': (95, 82, 50),
    'warm temperate thorn scrub': (77, 81, 48),
    'subtropical thorn woodland': (27, 40, 12),
    'tropical thorn woodland': (40, 62, 15),
    'tropical very dry forest': (87, 81, 49),
}

# ----------------
# Helper functions
# ----------------


def _elevation_color(elevation, sea_level=1.0):
    """
    Calculate color based on elevation
    :param elevation:
    :return:
    """
    color_step = 1.5
    if sea_level is None:
        sea_level = -1
    if elevation < sea_level/2:
        elevation /= sea_level
        return 0.0, 0.0, 0.75 + 0.5 * elevation
    elif elevation < sea_level:
        elevation /= sea_level
        return 0.0, 2 * (elevation - 0.5), 1.0
    else:
        elevation -= sea_level
        if elevation < 1.0 * color_step:
            return (0.0, 0.5 +
                    0.5 * elevation / color_step, 0.0)
        elif elevation < 1.5 * color_step:
            return 2 * (elevation - 1.0 * color_step) / color_step, 1.0, 0.0
        elif elevation < 2.0 * color_step:
            return 1.0, 1.0 - (elevation - 1.5 * color_step) / color_step, 0
        elif elevation < 3.0 * color_step:
            return (1.0 - 0.5 * (elevation - 2.0 *
                                 color_step) / color_step,
                    0.5 - 0.25 * (elevation - 2.0 *
                                  color_step) / color_step, 0)
        elif elevation < 5.0 * color_step:
            return (0.5 - 0.125 * (elevation - 3.0 *
                                   color_step) / (2 * color_step),
                    0.25 + 0.125 * (elevation - 3.0 *
                                    color_step) / (2 * color_step),
                    0.375 * (elevation - 3.0 *
                             color_step) / (2 * color_step))
        elif elevation < 8.0 * color_step:
            return (0.375 + 0.625 * (elevation - 5.0 *
                                     color_step) / (3 * color_step),
                    0.375 + 0.625 * (elevation - 5.0 *
                                     color_step) / (3 * color_step),
                    0.375 + 0.625 * (elevation - 5.0 *
                                     color_step) / (3 * color_step))
        else:
            elevation -= 8.0 * color_step
            while elevation > 2.0 * color_step:
                elevation -= 2.0 * color_step
            return 1, 1 - elevation / 4.0, 1


def _sature_color(color):
    r, g, b = color
    if r < 0:
        r = 0.0
    if r > 1.0:
        r = 1.0
    if g < 0:
        g = 0.0
    if g > 1.0:
        g = 1.0
    if b < 0:
        b = 0.0
    if b > 1.0:
        b = 1.0
    return r, g, b


def elevation_color(elevation, sea_level=1.0):
    return _sature_color(_elevation_color(elevation, sea_level))

def add_colors(*args):
    ''' Do some *args magic to return a tuple, which has the sums of all tuples in *args '''
    # Adapted from an answer here: http://stackoverflow.com/questions/14180866/sum-each-value-in-a-list-of-tuples
    added = [sum(x) for x in zip(*args)]
    return numpy.clip(added, 0, 255)  # restrict to uint8

def average_colors(c1, c2):
    ''' Average the values of two colors together '''
    r = int((c1[0] + c2[0])/2)
    g = int((c1[1] + c2[1])/2)
    b = int((c1[2] + c2[2])/2)

    return (r, g, b)

def get_normalized_elevation_array(world):
    ''' Convert raw elevation into normalized values between 0 and 255,
        and return a numpy array of these values '''

    e = world.elevation['data']

    mask = numpy.ma.array(e, mask=world.ocean)  # only land
    min_elev_land = mask.min()
    max_elev_land = mask.max()
    elev_delta_land = max_elev_land - min_elev_land

    mask = numpy.ma.array(e, mask=numpy.logical_not(world.ocean))  # only ocean
    min_elev_sea = mask.min()
    max_elev_sea = mask.max()
    elev_delta_sea = max_elev_sea - min_elev_sea

    c = numpy.empty(e.shape, dtype=numpy.float)
    c[numpy.invert(world.ocean)] = (e[numpy.invert(world.ocean)] - min_elev_land) * 127 / elev_delta_land + 128
    c[world.ocean] = (e[world.ocean] - min_elev_sea) * 127 / elev_delta_sea
    c = numpy.rint(c).astype(dtype=numpy.int32)  # proper rounding

    return c


def get_biome_color_based_on_elevation(world, elev, x, y, rng):
    ''' This is the "business logic" for determining the base biome color in satellite view.
        This includes generating some "noise" at each spot in a pixel's rgb value, potentially 
        modifying the noise based on elevation, and finally incorporating this with the base biome color. 

        The basic rules regarding noise generation are:
        - Oceans have no noise added
        - land tiles start with noise somewhere inside (-NOISE_RANGE, NOISE_RANGE) for each rgb value
        - land tiles with high elevations further modify the noise by set amounts (to drain some of the 
          color and make the map look more like mountains) 

        The biome's base color may be interpolated with a predefined mountain brown color if the elevation is high enough.

        Finally, the noise plus the biome color are added and returned.

        rng refers to an instance of a random number generator used to draw the random samples needed by this function.
    '''
    v = world.biome[y, x]
    biome_color = _biome_satellite_colors[v]

    # Default is no noise - will be overwritten if this tile is land
    noise = (0, 0, 0)

    if world.is_land((x, y)):
        ## Generate some random noise to apply to this pixel
        #  There is noise for each element of the rgb value
        #  This noise will be further modified by the height of this tile

        noise = rng.randint(-NOISE_RANGE, NOISE_RANGE, size=3)  # draw three random numbers at once

        ####### Case 1 - elevation is very high ########
        if elev > HIGH_MOUNTAIN_ELEV:     
            # Modify the noise to make the area slightly brighter to simulate snow-topped mountains.
            noise = add_colors(noise, HIGH_MOUNTAIN_NOISE_MODIFIER)
            # Average the biome's color with the MOUNTAIN_COLOR to tint the terrain
            biome_color = average_colors(biome_color, MOUNTAIN_COLOR)

        ####### Case 2 - elevation is high ########
        elif elev > MOUNTAIN_ELEV:   
            # Modify the noise to make this tile slightly darker, especially draining the green
            noise = add_colors(noise, MOUNTAIN_NOISE_MODIFIER)
            # Average the biome's color with the MOUNTAIN_COLOR to tint the terrain
            biome_color = average_colors(biome_color, MOUNTAIN_COLOR)

        ####### Case 3 - elevation is somewhat high ########
        elif elev > HIGH_HILL_ELEV:   
            noise = add_colors(noise, HIGH_HILL_NOISE_MODIFIER)

        ####### Case 4 - elevation is a little bit high ########
        elif elev > HILL_ELEV:   
            noise = add_colors(noise, HILL_NOISE_MODIFIER)

    # There is also a minor base modifier to the pixel's rgb value based on height
    modification_amount = int(elev / BASE_ELEVATION_INTENSITY_MODIFIER)
    base_elevation_modifier = (modification_amount, modification_amount, modification_amount)

    this_tile_color = add_colors(biome_color, noise, base_elevation_modifier)
    return this_tile_color


# ----------------------
# Draw on generic target
# ----------------------

def draw_simple_elevation(world, sea_level, target):
    """ This function can be used on a generic canvas (either an image to save
        on disk or a canvas part of a GUI)
    """
    e = world.elevation['data']
    c = numpy.empty(e.shape, dtype=numpy.float)

    has_ocean = not (sea_level is None or world.ocean is None or not world.ocean.any())  # or 'not any ocean'
    mask_land = numpy.ma.array(e, mask=world.ocean if has_ocean else False)  # only land

    min_elev_land = mask_land.min()
    max_elev_land = mask_land.max()
    elev_delta_land = (max_elev_land - min_elev_land) / 11.0

    if has_ocean:
        land = numpy.logical_not(world.ocean)
        mask_ocean = numpy.ma.array(e, mask=land)  # only ocean
        min_elev_sea = mask_ocean.min()
        max_elev_sea = mask_ocean.max()
        elev_delta_sea = max_elev_sea - min_elev_sea

        c[world.ocean] = ((e[world.ocean] - min_elev_sea) / elev_delta_sea)
        c[land] = ((e[land] - min_elev_land) / elev_delta_land) + 1
    else:
        c = ((e - min_elev_land) / elev_delta_land) + 1

    for y in range(world.height):
        for x in range(world.width):
            r, g, b = elevation_color(c[y, x], sea_level)
            target.set_pixel(x, y, (int(r * 255), int(g * 255),
                                    int(b * 255), 255))


def draw_riversmap(world, target):
    sea_color = (255, 255, 255, 255)
    land_color = (0, 0, 0, 255)

    for y in range(world.height):
        for x in range(world.width):
            target.set_pixel(x, y, sea_color if world.is_ocean((x, y)) else land_color)

    draw_rivers_on_image(world, target, factor=1)


def draw_grayscale_heightmap(world, target):
    c = get_normalized_elevation_array(world)

    for y in range(world.height):
        for x in range(world.width):
            target.set_pixel(x, y, (c[y, x], c[y, x], c[y, x], 255))


def draw_satellite(world, target):
    ''' This draws a "satellite map" - a view of the generated planet as it may look from space '''

    # Get an elevation mask where heights are normalized between 0 and 255
    elevation_mask = get_normalized_elevation_array(world)
    smooth_mask = numpy.invert(world.ocean)  # all land shall be smoothed (other tiles can be included by setting them to True)

    rng = numpy.random.RandomState(world.seed)  # create our own random generator; necessary for now to make the tests reproducible, even though it is a bit ugly

    ## The first loop sets each pixel's color based on colors defined in _biome_satellite_colors
    #  and additional "business logic" defined in get_biome_color_based_on_elevation
    for y in range(world.height):
        for x in range(world.width):
            # Get the normalized elevation at this pixel
            elev = elevation_mask[y, x]
            
            # Get a rgb noise value, with some logic to modify it based on the elevation of the tile
            r, g, b = get_biome_color_based_on_elevation(world, elev, x, y, rng)

            # Set pixel to this color. This initial color will be accessed and modified later when 
            # the map is smoothed and shaded.
            target.set_pixel(x, y, (r, g, b, 255))

    # Paint frozen areas.
    ice_color_variation = int(30)  # 0 means perfectly white ice; must be in [0, 255]; only affects R- and G-channel
    for y in range(world.height):
        for x in range(world.width):
            if world.icecap[y, x] > 0.0:
                smooth_mask[y, x] = True  # smooth the frozen areas, too
                variation = rng.randint(0, ice_color_variation)
                target.set_pixel(x, y, (255 - ice_color_variation + variation, 255 - ice_color_variation + variation, 255, 255))

    # Loop through and average a pixel with its neighbors to smooth transitions between biomes
    for y in range(1, world.height-1):
        for x in range(1, world.width-1):
            ## Only smooth land tiles
            if smooth_mask[y, x]:
                # Lists to hold the separated rgb values of the neighboring pixels
                all_r = []
                all_g = []
                all_b = []

                # Loop through this pixel and all neighboring pixels
                for j in range(y-1, y+2):
                    for i in range(x-1, x+2):
                        # Don't include ocean in the smoothing, if this tile happens to border an ocean
                        if smooth_mask[j, i]:
                            # Grab each rgb value and append to the list
                            r, g, b, a = target[j, i]
                            all_r.append(r)
                            all_g.append(g)
                            all_b.append(b)

                # Making sure there is at least one valid tile to be smoothed before we attempt to average the values
                if len(all_r) > 0:
                    avg_r = int(sum(all_r) / len(all_r))
                    avg_g = int(sum(all_g) / len(all_g))
                    avg_b = int(sum(all_b) / len(all_b))

                    ## Setting color of the pixel again - this will be once more modified by the shading algorithm
                    target.set_pixel(x, y, (avg_r, avg_g, avg_b, 255))

    ## After smoothing, draw rivers
    for y in range(world.height):
        for x in range(world.width):
            ## Color rivers
            if world.is_land((x, y)) and (world.river_map[y, x] > 0.0):
                base_color = target[y, x]

                r, g, b = add_colors(base_color, RIVER_COLOR_CHANGE)
                target.set_pixel(x, y, (r, g, b, 255))

            ## Color lakes
            if world.is_land((x, y)) and (world.lake_map[y, x] != 0):
                base_color = target[y, x]

                r, g, b = add_colors(base_color, LAKE_COLOR_CHANGE)
                target.set_pixel(x, y, (r, g, b, 255))

    # "Shade" the map by sending beams of light west to east, and increasing or decreasing value of pixel based on elevation difference
    for y in range(SAT_SHADOW_SIZE-1, world.height-SAT_SHADOW_SIZE-1):
        for x in range(SAT_SHADOW_SIZE-1, world.width-SAT_SHADOW_SIZE-1):
            if world.is_land((x, y)):
                r, g, b, a = target[y, x]
                
                # Build up list of elevations in the previous n tiles, where n is the shadow size.
                # This goes northwest to southeast
                prev_elevs = [ world.elevation['data'][y-n, x-n] for n in range(1, SAT_SHADOW_SIZE+1) ]

                # Take the average of the height of the previous n tiles
                avg_prev_elev = int( sum(prev_elevs) / len(prev_elevs) )

                # Find the difference between this tile's elevation, and the average of the previous elevations
                difference = int(world.elevation['data'][y, x] - avg_prev_elev)

                # Amplify the difference
                adjusted_difference = difference * SAT_SHADOW_DISTANCE_MULTIPLIER

                # The amplified difference is now translated into the rgb of the tile.
                # This adds light to tiles higher that the previous average, and shadow
                # to tiles lower than the previous average
                r = numpy.clip(adjusted_difference + r, 0, 255)  # prevent under-/overflows
                g = numpy.clip(adjusted_difference + g, 0, 255)
                b = numpy.clip(adjusted_difference + b, 0, 255)

                # Set the final color for this pixel
                target.set_pixel(x, y, (r, g, b, 255))


def draw_elevation(world, shadow, target):
    width = world.width
    height = world.height

    data = world.elevation['data']
    ocean = world.ocean

    mask = numpy.ma.array(data, mask=ocean)

    min_elev = mask.min()
    max_elev = mask.max()
    elev_delta = max_elev - min_elev

    for y in range(height):
        for x in range(width):
            if ocean[y, x]:
                target.set_pixel(x, y, (0, 0, 255, 255))
            else:
                e = data[y, x]
                c = 255 - int(((e - min_elev) * 255) / elev_delta)
                if shadow and y > 2 and x > 2:
                    if data[y - 1, x - 1] > e:
                        c -= 15
                    if data[y - 2, x - 2] > e \
                            and data[y - 2, x - 2] > data[y - 1, x - 1]:
                        c -= 10
                    if data[y - 3, x - 3] > e \
                            and data[y - 3, x - 3] > data[y - 1, x - 1] \
                            and data[y - 3, x - 3] > data[y - 2, x - 2]:
                        c -= 5
                    if c < 0:
                        c = 0
                target.set_pixel(x, y, (c, c, c, 255))


def draw_ocean(ocean, target):
    height, width = ocean.shape

    for y in range(height):
        for x in range(width):
            if ocean[y, x]:
                target.set_pixel(x, y, (0, 0, 255, 255))
            else:
                target.set_pixel(x, y, (0, 255, 255, 255))


def draw_precipitation(world, target, black_and_white=False):
    # FIXME we are drawing humidity, not precipitations
    width = world.width
    height = world.height

    if black_and_white:
        low = world.precipitation['data'].min()
        high = world.precipitation['data'].max()
        floor = 0
        ceiling = 255  # could be changed into 16 Bit grayscale easily

        colors = numpy.interp(world.precipitation['data'], [low, high], [floor, ceiling])
        colors = numpy.rint(colors).astype(dtype=numpy.int32)  # proper rounding
        for y in range(height):
            for x in range(width):
                target.set_pixel(x, y, (colors[y, x], colors[y, x], colors[y, x], 255))
    else:
        for y in range(height):
            for x in range(width):
                if world.is_humidity_superarid((x, y)):
                    target.set_pixel(x, y, (0, 32, 32, 255))
                elif world.is_humidity_perarid((x, y)):
                    target.set_pixel(x, y, (0, 64, 64, 255))
                elif world.is_humidity_arid((x, y)):
                    target.set_pixel(x, y, (0, 96, 96, 255))
                elif world.is_humidity_semiarid((x, y)):
                    target.set_pixel(x, y, (0, 128, 128, 255))
                elif world.is_humidity_subhumid((x, y)):
                    target.set_pixel(x, y, (0, 160, 160, 255))
                elif world.is_humidity_humid((x, y)):
                    target.set_pixel(x, y, (0, 192, 192, 255))
                elif world.is_humidity_perhumid((x, y)):
                    target.set_pixel(x, y, (0, 224, 224, 255))
                elif world.is_humidity_superhumid((x, y)):
                    target.set_pixel(x, y, (0, 255, 255, 255))


def draw_world(world, target):
    width = world.width
    height = world.height

    for y in range(height):
        for x in range(width):
            if world.is_land((x, y)):
                biome = world.biome_at((x, y))
                target.set_pixel(x, y, _biome_colors[biome.name()])
            else:
                c = int(world.sea_depth[y, x] * 200 + 50)
                target.set_pixel(x, y, (0, 0, 255 - c, 255))


def draw_temperature_levels(world, target, black_and_white=False):
    width = world.width
    height = world.height

    if black_and_white:
        low = world.temperature_thresholds()[0][1]
        high = world.temperature_thresholds()[5][1]
        floor = 0
        ceiling = 255  # could be changed into 16 Bit grayscale easily

        colors = numpy.interp(world.temperature['data'], [low, high], [floor, ceiling])
        colors = numpy.rint(colors).astype(dtype=numpy.int32)  # proper rounding
        for y in range(height):
            for x in range(width):
                target.set_pixel(x, y, (colors[y, x], colors[y, x], colors[y, x], 255))

    else:
        for y in range(height):
            for x in range(width):
                if world.is_temperature_polar((x, y)):
                    target.set_pixel(x, y, (0, 0, 255, 255))
                elif world.is_temperature_alpine((x, y)):
                    target.set_pixel(x, y, (42, 0, 213, 255))
                elif world.is_temperature_boreal((x, y)):
                    target.set_pixel(x, y, (85, 0, 170, 255))
                elif world.is_temperature_cool((x, y)):
                    target.set_pixel(x, y, (128, 0, 128, 255))
                elif world.is_temperature_warm((x, y)):
                    target.set_pixel(x, y, (170, 0, 85, 255))
                elif world.is_temperature_subtropical((x, y)):
                    target.set_pixel(x, y, (213, 0, 42, 255))
                elif world.is_temperature_tropical((x, y)):
                    target.set_pixel(x, y, (255, 0, 0, 255))


def draw_biome(world, target):
    width = world.width
    height = world.height

    biome = world.biome

    for y in range(height):
        for x in range(width):
            v = biome[y, x]
            target.set_pixel(x, y, _biome_colors[v])


def draw_scatter_plot(world, size, target):
    """ This function can be used on a generic canvas (either an image to save
        on disk or a canvas part of a GUI)
    """

    #Find min and max values of humidity and temperature on land so we can
    #normalize temperature and humidity to the chart
    humid = numpy.ma.masked_array(world.humidity['data'], mask=world.ocean)
    temp = numpy.ma.masked_array(world.temperature['data'], mask=world.ocean)
    min_humidity = humid.min()
    max_humidity = humid.max()
    min_temperature = temp.min()
    max_temperature = temp.max()
    temperature_delta = max_temperature - min_temperature
    humidity_delta = max_humidity - min_humidity
    
    #set all pixels white
    for y in range(0, size):
        for x in range(0, size):
            target.set_pixel(x, y, (255, 255, 255, 255))

    #fill in 'bad' boxes with grey
    h_values = ['62', '50', '37', '25', '12']
    t_values = [   0,    1,    2,   3,    5 ]
    for loop in range(0, 5):
        h_min = (size - 1) * ((world.humidity['quantiles'][h_values[loop]] - min_humidity) / humidity_delta)
        if loop != 4:
            h_max = (size - 1) * ((world.humidity['quantiles'][h_values[loop + 1]] - min_humidity) / humidity_delta)
        else:
            h_max = size
        v_max = (size - 1) * ((world.temperature['thresholds'][t_values[loop]][1] - min_temperature) / temperature_delta)
        if h_min < 0:
            h_min = 0
        if h_max > size:
            h_max = size
        if v_max < 0:
            v_max = 0
        if v_max > (size - 1):
            v_max = size - 1
            
        if h_max > 0 and h_min < size and v_max > 0:
            for y in range(int(h_min), int(h_max)):
                for x in range(0, int(v_max)):
                    target.set_pixel(x, (size - 1) - y, (128, 128, 128, 255))
                    
    #draw lines based on thresholds
    for t in range(0, 6):
        v = (size - 1) * ((world.temperature['thresholds'][t][1] - min_temperature) / temperature_delta)
        if 0 < v < size:
            for y in range(0, size):
                target.set_pixel(int(v), (size - 1) - y, (0, 0, 0, 255))
    ranges = ['87', '75', '62', '50', '37', '25', '12']
    for p in ranges:
        h = (size - 1) * ((world.humidity['quantiles'][p] - min_humidity) / humidity_delta)
        if 0 < h < size:
            for x in range(0, size):
                target.set_pixel(x, (size - 1) - int(h), (0, 0, 0, 255))

    #draw gamma curve
    curve_gamma = world.gamma_curve
    curve_bonus = world.curve_offset
    
    for x in range(0, size):
        y = (size - 1) * ((numpy.power((float(x) / (size - 1)), curve_gamma) * (1 - curve_bonus)) + curve_bonus)
        target.set_pixel(x, (size - 1) - int(y), (255, 0, 0, 255))

    #examine all cells in the map and if it is land get the temperature and
    #humidity for the cell.
    for y in range(world.height):
        for x in range(world.width):
            if world.is_land((x, y)):
                t = world.temperature_at((x, y))
                p = world.humidity['data'][y, x]

    #get red and blue values depending on temperature and humidity                
                if world.is_temperature_polar((x, y)):
                    r = 0
                elif world.is_temperature_alpine((x, y)):
                    r = 42
                elif world.is_temperature_boreal((x, y)):
                    r = 85
                elif world.is_temperature_cool((x, y)):
                    r = 128
                elif world.is_temperature_warm((x, y)):
                    r = 170
                elif world.is_temperature_subtropical((x, y)):
                    r = 213
                elif world.is_temperature_tropical((x, y)):
                    r = 255
                if world.is_humidity_superarid((x, y)):
                    b = 32
                elif world.is_humidity_perarid((x, y)):
                    b = 64
                elif world.is_humidity_arid((x, y)):
                    b = 96
                elif world.is_humidity_semiarid((x, y)):
                    b = 128
                elif world.is_humidity_subhumid((x, y)):
                    b = 160
                elif world.is_humidity_humid((x, y)):
                    b = 192
                elif world.is_humidity_perhumid((x, y)):
                    b = 224
                elif world.is_humidity_superhumid((x, y)):
                    b = 255

    #calculate x and y position based on normalized temperature and humidity
                nx = (size - 1) * ((t - min_temperature) / temperature_delta)
                ny = (size - 1) * ((p - min_humidity) / humidity_delta)
                    
                target.set_pixel(int(nx), (size - 1) - int(ny), (r, 128, b, 255))
    

# -------------
# Draw on files
# -------------


def draw_simple_elevation_on_file(world, filename, sea_level):
    img = PNGWriter.rgba_from_dimensions(world.width, world.height, filename)
    draw_simple_elevation(world, sea_level, img)
    img.complete()


def draw_riversmap_on_file(world, filename):
    img = PNGWriter.rgba_from_dimensions(world.width, world.height, filename)
    draw_riversmap(world, img)
    img.complete()


def draw_grayscale_heightmap_on_file(world, filename):
    img = PNGWriter.grayscale_from_array(world.elevation['data'], filename, scale_to_range=True)
    #draw_grayscale_heightmap(world, img)
    img.complete()


def draw_elevation_on_file(world, filename, shadow=True):
    img = PNGWriter.rgba_from_dimensions(world.width, world.height, filename)
    draw_elevation(world, shadow, img)
    img.complete()


def draw_ocean_on_file(ocean, filename):
    height, width = ocean.shape
    img = PNGWriter.rgba_from_dimensions(width, height, filename)
    draw_ocean(ocean, img)
    img.complete()


def draw_precipitation_on_file(world, filename, black_and_white=False):
    img = PNGWriter.rgba_from_dimensions(world.width, world.height, filename)
    draw_precipitation(world, img, black_and_white)
    img.complete()


def draw_world_on_file(world, filename):
    img = PNGWriter.rgba_from_dimensions(world.width, world.height, filename)
    draw_world(world, img)
    img.complete()


def draw_temperature_levels_on_file(world, filename, black_and_white=False):
    img = PNGWriter.rgba_from_dimensions(world.width, world.height, filename)
    draw_temperature_levels(world, img, black_and_white)
    img.complete()


def draw_biome_on_file(world, filename):
    img = PNGWriter.rgba_from_dimensions(world.width, world.height, filename)
    draw_biome(world, img)
    img.complete()


def draw_ancientmap_on_file(world, filename, resize_factor=1,
                            sea_color=(212, 198, 169, 255),
                            draw_biome=True, draw_rivers=True, draw_mountains=True, 
                            draw_outer_land_border=False, verbose=False):
    img = PNGWriter.rgba_from_dimensions(world.width * resize_factor, world.height * resize_factor, filename)
    draw_ancientmap(world, img, resize_factor, sea_color,
                    draw_biome, draw_rivers, draw_mountains, draw_outer_land_border, 
                    verbose)
    img.complete()


def draw_scatter_plot_on_file(world, filename):
    img = PNGWriter.rgba_from_dimensions(512, 512, filename)
    draw_scatter_plot(world, 512, img)
    img.complete()


def draw_satellite_on_file(world, filename):
    img = PNGWriter.rgba_from_dimensions(world.width, world.height, filename)
    draw_satellite(world, img)
    img.complete()


def draw_icecaps_on_file(world, filename):
    img = PNGWriter.grayscale_from_array(world.icecap, filename, scale_to_range=True)
    img.complete()
