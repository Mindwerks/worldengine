"""
This file should contain only functions that operates on pixels, not on images,
so no references to PIL are necessary and the module can be used also through
Jython
"""

import numpy
import sys
import time
from worldengine.common import get_verbose, count_neighbours
from worldengine.common import anti_alias as anti_alias_channel
from worldengine.biome import BiomeGroup, _un_camelize


# -------------------
# Reusable functions
# -------------------


def gradient(value, low, high, low_color, high_color):
    lr, lg, lb = low_color
    if high == low:
        return lr, lg, lb, 255
    _range = float(high - low)
    _x = float(value - low) / _range
    _ix = 1.0 - _x
    hr, hg, hb = high_color
    r = int(lr * _ix + hr * _x)
    g = int(lg * _ix + hg * _x)
    b = int(lb * _ix + hb * _x)
    return r, g, b, 255


def rgba_to_rgb(rgba):
    r, g, b, a = rgba
    return r, g, b


def draw_rivers_on_image(world, target, factor=1):
    """Draw only the rivers, it expect the background to be in place
    """

    for y in range(world.height):
        for x in range(world.width):
            if world.is_land((x, y)) and (world.layers['river_map'].data[y, x] > 0.0):
                for dx in range(factor):
                    for dy in range(factor):
                        target.set_pixel(x * factor + dx, y * factor + dy, (0, 0, 128, 255))
            if world.is_land((x, y)) and (world.layers['lake_map'].data[y, x] != 0):
                for dx in range(factor):
                    for dy in range(factor):
                        target.set_pixel(x * factor + dx, y * factor + dy, (0, 100, 128, 255))


# -------------------
# Drawing ancient map
# -------------------

def _find_mountains_mask(world, factor):
    _mask = numpy.zeros((world.height, world.width), float)
    _mask[world.elevation>world.get_mountain_level()] = 1.0

    # disregard elevated oceans
    _mask[world.ocean] = 0.0

    # this is fast but not 100% precise
    # subsequent steps are fiendishly sensitive to these precision errors
    # therefore the rounding
    _mask[_mask>0] = numpy.around(count_neighbours(_mask, 3)[_mask>0], 6)

    _mask[_mask<32.000000001] = 0.0
    _mask /= 4.0
    _mask = _mask.repeat(factor, 0).repeat(factor, 1)

    return _mask


def _build_biome_group_masks(world, factor):

    biome_groups = BiomeGroup.__subclasses__()

    biome_masks = {}

    for group in biome_groups:
        group_mask = numpy.zeros((world.height, world.width), float)

        for biome in group.__subclasses__():
            group_mask[world.biome==_un_camelize(biome.__name__)] += 1.0
               
        group_mask[group_mask>0] = count_neighbours(group_mask)[group_mask>0]

        group_mask[group_mask<5.000000001] = 0.0

        group_mask = group_mask.repeat(factor, 0).repeat(factor, 1)

        biome_masks[_un_camelize(group.__name__)] = group_mask

    return biome_masks

def _draw_shaded_pixel(pixels, x, y, r, g, b):
    nb = (x ** int(y / 5) + x * 23 + y * 37 + (x * y) * 13) % 75
    nr = r - nb
    ng = g - nb
    nb = b - nb
    pixels[y, x] = (nr, ng, nb, 255)


def _draw_forest_pattern1(pixels, x, y, c, c2):
    pixels[y - 4, x + 0] = c
    pixels[y - 3, x + 0] = c
    pixels[y - 2, x - 1] = c
    pixels[y - 2, x + 1] = c
    pixels[y - 1, x - 1] = c
    pixels[y - 1, x + 1] = c
    pixels[y + 0, x - 2] = c
    pixels[y + 0, x + 1] = c
    pixels[y + 0, x + 2] = c
    pixels[y + 1, x - 2] = c
    pixels[y + 1, x + 2] = c
    pixels[y + 2, x - 3] = c
    pixels[y + 2, x - 1] = c
    pixels[y + 2, x + 3] = c
    pixels[y + 3, x - 3] = c
    pixels[y + 3, x - 2] = c
    pixels[y + 3, x - 1] = c
    pixels[y + 3, x - 0] = c
    pixels[y + 3, x + 1] = c
    pixels[y + 3, x + 2] = c
    pixels[y + 3, x + 3] = c
    pixels[y + 4, x - 0] = c

    pixels[y - 2, x + 0] = c2
    pixels[y - 1, x + 0] = c2
    pixels[y - 0, x - 1] = c2
    pixels[y - 0, x - 0] = c2
    pixels[y + 1, x - 1] = c2
    pixels[y + 1, x - 0] = c2
    pixels[y + 1, x + 1] = c2
    pixels[y + 2, x - 2] = c2
    pixels[y + 2, x - 0] = c2
    pixels[y + 2, x + 1] = c2
    pixels[y + 2, x + 2] = c2


def _draw_forest_pattern2(pixels, x, y, c, c2):
    pixels[y - 4, x - 1] = c
    pixels[y - 4, x - 0] = c
    pixels[y - 4, x + 1] = c
    pixels[y - 3, x - 2] = c
    pixels[y - 3, x - 1] = c
    pixels[y - 3, x + 2] = c
    pixels[y - 2, x - 2] = c
    pixels[y - 2, x + 1] = c
    pixels[y - 2, x + 2] = c
    pixels[y - 1, x - 2] = c
    pixels[y - 1, x + 2] = c
    pixels[y - 0, x - 2] = c
    pixels[y - 0, x - 1] = c
    pixels[y - 0, x + 2] = c
    pixels[y + 1, x - 2] = c
    pixels[y + 1, x + 1] = c
    pixels[y + 1, x + 2] = c
    pixels[y + 2, x - 1] = c
    pixels[y + 2, x - 0] = c
    pixels[y + 2, x + 1] = c
    pixels[y + 3, x - 0] = c
    pixels[y + 4, x - 0] = c

    pixels[y - 3, x + 0] = c2
    pixels[y - 3, x + 1] = c2
    pixels[y - 2, x - 1] = c2
    pixels[y - 2, x - 0] = c2
    pixels[y - 1, x - 1] = c2
    pixels[y - 1, x - 0] = c2
    pixels[y - 1, x + 1] = c2
    pixels[y - 0, x - 0] = c2
    pixels[y - 0, x + 1] = c2
    pixels[y + 1, x - 1] = c2
    pixels[y + 1, x - 0] = c2


def _draw_desert_pattern(pixels, x, y, c):
    pixels[y - 2, x - 1] = c
    pixels[y - 2, x - 0] = c
    pixels[y - 2, x + 1] = c
    pixels[y - 2, x + 1] = c
    pixels[y - 2, x + 2] = c
    pixels[y - 1, x - 2] = c
    pixels[y - 1, x - 1] = c
    pixels[y - 1, x - 0] = c
    pixels[y - 1, x + 4] = c
    pixels[y - 0, x - 4] = c
    pixels[y - 0, x - 3] = c
    pixels[y - 0, x - 2] = c
    pixels[y - 0, x - 1] = c
    pixels[y - 0, x + 1] = c
    pixels[y - 0, x + 2] = c
    pixels[y - 0, x + 6] = c
    pixels[y + 1, x - 5] = c
    pixels[y + 1, x - 0] = c
    pixels[y + 1, x + 7] = c
    pixels[y + 1, x + 8] = c
    pixels[y + 2, x - 8] = c
    pixels[y + 2, x - 7] = c


def _draw_glacier(pixels, x, y):
    rg = 255 - (x ** int(y / 5) + x * 23 + y * 37 + (x * y) * 13) % 75
    pixels[y, x] = (rg, rg, 255, 255)


def _draw_cold_parklands(pixels, x, y, w, h):
    b = (x ** int(y / 5) + x * 23 + y * 37 + (x * y) * 13) % 75
    r = 105 - b
    g = 96 - b
    b = 38 - int(b / 2)
    pixels[y, x] = (r, g, b, 255)


def _draw_boreal_forest(pixels, x, y, w, h):
    c = (0, 32, 0, 255)
    c2 = (0, 64, 0, 255)
    _draw_forest_pattern1(pixels, x, y, c, c2)


def _draw_warm_temperate_forest(pixels, x, y, w, h):
    c = (0, 96, 0, 255)
    c2 = (0, 192, 0, 255)
    _draw_forest_pattern2(pixels, x, y, c, c2)
    

def _draw_temperate_forest1(pixels, x, y, w, h):
    c = (0, 64, 0, 255)
    c2 = (0, 96, 0, 255)
    _draw_forest_pattern1(pixels, x, y, c, c2)


def _draw_temperate_forest2(pixels, x, y, w, h):
    c = (0, 64, 0, 255)
    c2 = (0, 112, 0, 255)
    _draw_forest_pattern2(pixels, x, y, c, c2)


def _draw_tropical_dry_forest(pixels, x, y, w, h):
    c = (51, 36, 3, 255)
    c2 = (139, 204, 58, 255)
    _draw_forest_pattern2(pixels, x, y, c, c2)


def _draw_jungle(pixels, x, y, w, h):
    c = (0, 128, 0, 255)
    c2 = (0, 255, 0, 255)
    _draw_forest_pattern2(pixels, x, y, c, c2)


def _draw_cool_desert(pixels, x, y, w, h):
    c = (72, 72, 53, 255)
    # c2 = (219, 220, 200, 255)  # TODO: not used?
    _draw_desert_pattern(pixels, x, y, c)
    
    
def _draw_hot_desert(pixels, x, y, w, h):
    c = (72, 72, 53, 255)
    # c2 = (219, 220, 200, 255)  # TODO: not used?
    _draw_desert_pattern(pixels, x, y, c)  


def _draw_tundra(pixels, x, y, w, h):
    _draw_shaded_pixel(pixels,x, y, 166, 148, 75)


def _draw_steppe(pixels, x, y, w, h):
    _draw_shaded_pixel(pixels, x, y, 96, 192, 96)


def _draw_chaparral(pixels, x, y, w, h):
    _draw_shaded_pixel(pixels, x, y, 180, 171, 113)


def _draw_savanna(pixels, x, y, w, h):
    _draw_shaded_pixel(pixels, x, y, 255, 246, 188)


# TODO: complete and enable this one
def _dynamic_draw_a_mountain(pixels, rng, x, y, w=3, h=3):
    # mcl = (0, 0, 0, 255)  # TODO: No longer used?
    # mcll = (128, 128, 128, 255)
    mcr = (75, 75, 75, 255)
    # left edge
    last_leftborder = None
    for mody in range(-h, h + 1):
        bottomness = (float(mody + h) / 2.0) / w

        min_leftborder = int(bottomness * w * 0.66)
        if not last_leftborder == None:
            min_leftborder = max(min_leftborder, last_leftborder - 1)
        max_leftborder = int(bottomness * w * 1.33)
        if not last_leftborder == None:
            max_leftborder = min(max_leftborder, last_leftborder + 1)
        leftborder = int(bottomness * w) + rng.randint(-2, 2)/2
        if leftborder < min_leftborder:
            leftborder = min_leftborder
        if leftborder > max_leftborder:
            leftborder = max_leftborder
        last_leftborder = leftborder

        darkarea = int(bottomness * w / 2)
        lightarea = int(bottomness * w / 2)
        for itx in range(darkarea, leftborder + 1):
            pixels[y + mody, x - itx] = gradient(itx, darkarea, leftborder,
                                                 (0, 0, 0), (64, 64, 64))
        for itx in range(-darkarea, lightarea + 1):
            pixels[y + mody, x - itx] = gradient(itx, -darkarea, lightarea,
                                                 (64, 64, 64), (128, 128, 128))
        for itx in range(lightarea, leftborder):
            pixels[y + mody, x - itx] = (181, 166, 127, 255)  # land_color
    # right edge
    last_modx = None
    for mody in range(-h, h + 1):
        bottomness = (float(mody + h) / 2.0) / w
        min_modx = int(bottomness * w * 0.66)
        if not last_modx == None:
            min_modx = max(min_modx, last_modx - 1)
        max_modx = int(bottomness * w * 1.33)
        if not last_modx == None:
            max_modx = min(max_modx, last_modx + 1)
        modx = int(bottomness * w) + numpy.random.randint(-2, 2)/2
        if modx < min_modx:
            modx = min_modx
        if modx > max_modx:
            modx = max_modx
        last_modx = modx
        pixels[y + mody, x - itx] = mcr


def _draw_a_mountain(pixels, x, y, w=3, h=3):
    # mcl = (0, 0, 0, 255)  # TODO: No longer used?
    # mcll = (128, 128, 128, 255)
    mcr = (75, 75, 75, 255)
    # left edge
    for mody in range(-h, h + 1):
        bottomness = (float(mody + h) / 2.0) / w
        leftborder = int(bottomness * w)
        darkarea = int(bottomness * w / 2)
        lightarea = int(bottomness * w / 2)
        for itx in range(darkarea, leftborder + 1):
            pixels[y + mody, x - itx] = gradient(itx, darkarea, leftborder,
                                                 (0, 0, 0), (64, 64, 64))
        for itx in range(-darkarea, lightarea + 1):
            pixels[y + mody, x + itx] = gradient(itx, -darkarea, lightarea,
                                                 (64, 64, 64), (128, 128, 128))
        for itx in range(lightarea, leftborder):
            pixels[y + mody, x + itx] = (181, 166, 127, 255)  # land_color
    # right edge
    for mody in range(-h, h + 1):
        bottomness = (float(mody + h) / 2.0) / w
        modx = int(bottomness * w)
        pixels[y + mody, x + modx] = mcr      


def draw_ancientmap(world, target, resize_factor=1,
                    sea_color=(212, 198, 169, 255),
                    draw_biome = True, draw_rivers = True, draw_mountains = True,
                    draw_outer_land_border = False, verbose=get_verbose()):
    rng = numpy.random.RandomState(world.seed)  # create our own random generator

    if verbose:
        start_time = time.time()

    land_color = (
        181, 166, 127, 255)  # TODO: Put this in the argument list too??

    scaled_ocean = world.ocean.repeat(resize_factor, 0).repeat(resize_factor, 1)
    
    borders = numpy.zeros((resize_factor * world.height, resize_factor * world.width), bool)
    borders[count_neighbours(scaled_ocean) > 0] = True
    borders[scaled_ocean] = False

    # cache neighbours count at different radii
    border_neighbours = {}

    border_neighbours[6] = numpy.rint(count_neighbours(borders, 6))
    border_neighbours[9] = numpy.rint(count_neighbours(borders, 9))

    if draw_outer_land_border:
        inner_borders = borders
        outer_borders = None

        for i in range(2):
            _outer_borders =  numpy.zeros((resize_factor * world.height, resize_factor * world.width), bool)
            _outer_borders[count_neighbours(inner_borders) > 0] = True
            _outer_borders[inner_borders] = False
            _outer_borders[numpy.logical_not(scaled_ocean)] = False
            outer_borders = _outer_borders
            inner_borders = outer_borders

    if draw_mountains:
        mountains_mask = _find_mountains_mask(world, resize_factor)

    if draw_biome:
        biome_masks = _build_biome_group_masks(world, resize_factor)

        def _draw_biome(name, _func, w, h, r, _alt_func = None):
            if verbose:
                start_time = time.time()

            for y in range(resize_factor * world.height):
                for x in range(resize_factor * world.width):
                    if biome_masks[name][y, x] > 0:
                        if r == 0 or border_neighbours[r][y,x] <= 2:
                            if _alt_func is not None and rng.random_sample() > .5:
                                _alt_func(target, x, y, w, h)
                            else:
                                _func(target, x, y, w, h)
                            biome_masks[name][y-r:y+r+1,x-r:x+r+1] = 0.0

            if verbose:
                elapsed_time = time.time() - start_time
                print(
                    "...drawing_functions.draw_ancientmap: " + name +
                    " Elapsed time " + str(elapsed_time) + " seconds.")

    if verbose:
        elapsed_time = time.time() - start_time
        print(
            "...drawing_functions.draw_oldmap_on_pixel: init Elapsed time " +
            str(elapsed_time) + " seconds.")
        sys.stdout.flush()

    if verbose:
        start_time = time.time()

    border_color = (0, 0, 0, 255)
    outer_border_color = gradient(0.5, 0, 1.0, rgba_to_rgb(border_color), rgba_to_rgb(sea_color))

    # start in low resolution
    num_channels = 4
    channels = numpy.zeros((num_channels, world.height, world.width), int)

    for c in range(num_channels):
        channels[c] = land_color[c]
        channels[c][world.ocean] = sea_color[c]

    # now go full resolution
    channels = channels.repeat(resize_factor, 1).repeat(resize_factor, 2)

    if draw_outer_land_border:
        for c in range(num_channels):
            channels[c][outer_borders] = outer_border_color[c]

    for c in range(num_channels):
            channels[c][borders] = border_color[c]

    if verbose:
        elapsed_time = time.time() - start_time
        print(
            "...drawing_functions.draw_oldmap_on_pixel: color ocean " +
            "Elapsed time " + str(elapsed_time) + " seconds.")

    if verbose:
        start_time = time.time()

    # don't anti-alias the alpha channel
    for c in range(num_channels-1):
        channels[c] = anti_alias_channel(channels[c], 1)

    
    # switch from channel major storage to pixel major storage
    for c in range(num_channels):
        target[:,:,c] = channels[c,:,:]


    if verbose:
        elapsed_time = time.time() - start_time
        print(
            "...drawing_functions.draw_oldmap_on_pixel: anti alias " +
            "Elapsed time " + str(elapsed_time) + " seconds.")

    if draw_biome:
        # Draw glacier
        if verbose:
            start_time = time.time()
        for y in range(resize_factor * world.height):
            for x in range(resize_factor * world.width):
                if not borders[y, x] and world.is_iceland(
                        (int(x / resize_factor), int(y / resize_factor))):
                    _draw_glacier(target, x, y)
        if verbose:
            elapsed_time = time.time() - start_time
            print(
                "...drawing_functions.draw_oldmap_on_pixel: draw glacier " +
                "Elapsed time " + str(elapsed_time) + " seconds.")
       
        _draw_biome('tundra', _draw_tundra, 0, 0, 0) 
        _draw_biome('cold parklands', _draw_cold_parklands, 0, 0, 0) 
        _draw_biome('steppe', _draw_steppe, 0, 0, 0) 
        _draw_biome('chaparral', _draw_chaparral, 0, 0, 0) 
        _draw_biome('savanna', _draw_savanna, 0, 0, 0)  
        _draw_biome('cool desert', _draw_cool_desert, 8, 2, 9)
        _draw_biome('hot desert', _draw_hot_desert, 8, 2, 9)
        _draw_biome('boreal forest', _draw_boreal_forest, 4, 5, 6)
        _draw_biome('cool temperate forest', _draw_temperate_forest1, 4, 5, 6,
                    _draw_temperate_forest2)            
        _draw_biome('warm temperate forest', _draw_warm_temperate_forest, 4, 5, 6)  
        _draw_biome('tropical dry forest group', _draw_tropical_dry_forest, 4, 5, 6)
        _draw_biome('jungle', _draw_jungle, 4, 5, 6)

        # TODO: there was a stub for a rock desert biome group
        # it should be super easy to introduce that group with the new
        # biome group concept but since it did nothing I removed the stub

    if draw_rivers:
        draw_rivers_on_image(world, target, resize_factor)

    # Draw mountains
    if draw_mountains:
        if verbose:
            start_time = time.time()
        for y in range(resize_factor * world.height):
            for x in range(resize_factor * world.width):
                if mountains_mask[y, x] > 0:
                    w = mountains_mask[y, x]
                    h = 3 + int(world.level_of_mountain(
                        (int(x / resize_factor), int(y / resize_factor))))
                    r = max(int(w / 3 * 2), h)

                    if r not in border_neighbours:
                        border_neighbours[r] = numpy.rint(count_neighbours(borders, r))

                    if border_neighbours[r][y,x] <= 2:
                        _draw_a_mountain(target, x, y, w=w, h=h)
                        mountains_mask[y-r:y+r+1,x-r:x+r+1] = 0.0
        if verbose:
            elapsed_time = time.time() - start_time
            print(
                "...drawing_functions.draw_oldmap_on_pixel: draw mountains " +
                "Elapsed time " + str(elapsed_time) + " seconds.")
