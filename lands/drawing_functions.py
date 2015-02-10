"""
This file should contain only functions that operates on pixels, not on images,
so no references to PIL are necessary and the module can be used also through
Jython
"""

__author__ = 'Federico Tomassetti'

import random
import math
import sys
import time

if sys.version_info > (2,):
    xrange = range

def find_land_borders(world, factor):
    _ocean   = [[False for x in xrange(factor*world.width)] for y in xrange(factor*world.height)]
    _borders = [[False for x in xrange(factor*world.width)] for y in xrange(factor*world.height)]
    for y in xrange(world.height*factor):
        for x in xrange(world.width*factor):
            if world.ocean[int(y/factor)][int(x/factor)]:
                _ocean[y][x] = True

    def my_is_ocean(pos):
        x, y = pos
        return _ocean[y][x]

    for y in xrange(world.height*factor):
        for x in xrange(world.width*factor):
            if not _ocean[y][x] and world.tiles_around_factor(factor, (x, y), radius=1, predicate=my_is_ocean):
                _borders[y][x] = True
    return _borders


def find_mountains_mask(world, factor):
    _mask = [[False for x in xrange(factor*world.width)] for y in xrange(factor*world.height)]
    for y in xrange(factor*world.height):
        for x in xrange(factor*world.width):
            if world.is_mountain((int(x/factor), int(y/factor))):
                v = len(world.tiles_around((int(x/factor), int(y/factor)), radius=3, predicate=world.is_mountain))
                if v > 32:
                    _mask[y][x] = v / 4
    return _mask


def mask(world, predicate, factor):
    _mask = [[False for x in xrange(factor*world.width)] for y in xrange(factor*world.height)]
    for y in xrange(factor*world.height):
        for x in xrange(factor*world.width):
            xf = int(x/factor)
            yf = int(y/factor)
            if predicate((xf, yf)):
                v = len(world.tiles_around((xf, yf), radius=1, predicate=predicate))
                if v > 5:
                    _mask[y][x] = v
    return _mask


def find_boreal_forest_mask(world, factor):
    return mask(world, predicate=world.is_boreal_forest, factor=factor)

def find_temperate_forest_mask(world, factor):
    return mask(world, predicate=world.is_temperate_forest, factor=factor)

def find_warm_temperate_forest_mask(world, factor):
    return mask(world, predicate=world.is_warm_temperate_forest, factor=factor)

def find_tropical_dry_forest_mask(world, factor):
    return mask(world, predicate=world.is_tropical_dry_forest, factor=factor)


def gradient(value, low, high, low_color, high_color):
    if high == low:
        return low_color
    _range = float(high - low)
    _x = float(value - low) / _range
    _ix = 1.0 - _x
    lr, lg, lb = low_color
    hr, hg, hb = high_color
    r = int(lr * _ix + hr * _x)
    g = int(lg * _ix + hg * _x)
    b = int(lb * _ix + hb * _x)
    return (r, g, b, 255)

def draw_glacier(pixels, x, y):
    rg = 255 - (x ** int(y / 5) + x * 23 + y * 37 + (x * y) * 13) % 75
    pixels[x, y] = (rg, rg, 255, 255)

def draw_tundra(pixels, x, y):
    b = (x ** int(y / 5) + x * 23 + y * 37 + (x * y) * 13) % 75
    r = 166 - b
    g = 148 - b
    b = 75 - b
    pixels[x, y] = (r, g, b, 255)

def draw_cold_parklands(pixels, x, y):
    b = (x ** int(y / 5) + x * 23 + y * 37 + (x * y) * 13) % 75
    r = 105 - b
    g = 96 - b
    b = 38 - int(b / 2)
    pixels[x, y] = (r, g, b, 255)

def draw_boreal_forest(pixels, x, y, w, h):
    c = (0, 32, 0, 255)
    c2 = (0, 64, 0, 255)
    pixels[x + 0, y - 4] = c
    pixels[x + 0, y - 3] = c
    pixels[x - 1, y - 2] = c
    pixels[x + 1, y - 2] = c
    pixels[x - 1, y - 1] = c
    pixels[x + 1, y - 1] = c
    pixels[x - 2, y + 0] = c
    pixels[x + 1, y + 0] = c
    pixels[x + 2, y + 0] = c
    pixels[x - 2, y + 1] = c
    pixels[x + 2, y + 1] = c
    pixels[x - 3, y + 2] = c
    pixels[x - 1, y + 2] = c
    pixels[x + 3, y + 2] = c
    pixels[x - 3, y + 3] = c
    pixels[x - 2, y + 3] = c
    pixels[x - 1, y + 3] = c
    pixels[x - 0, y + 3] = c
    pixels[x + 1, y + 3] = c
    pixels[x + 2, y + 3] = c
    pixels[x + 3, y + 3] = c
    pixels[x - 0, y + 4] = c

    pixels[x + 0, y - 2] = c2
    pixels[x + 0, y - 1] = c2
    pixels[x - 1, y - 0] = c2
    pixels[x - 0, y - 0] = c2
    pixels[x - 1, y + 1] = c2
    pixels[x - 0, y + 1] = c2
    pixels[x + 1, y + 1] = c2
    pixels[x - 2, y + 2] = c2
    pixels[x - 0, y + 2] = c2
    pixels[x + 1, y + 2] = c2
    pixels[x + 2, y + 2] = c2

def draw_temperate_forest1(pixels, x, y, w, h):
    c = (0, 64, 0, 255)
    c2 = (0, 96, 0, 255)
    pixels[x + 0, y - 4] = c
    pixels[x + 0, y - 3] = c
    pixels[x - 1, y - 2] = c
    pixels[x + 1, y - 2] = c
    pixels[x - 1, y - 1] = c
    pixels[x + 1, y - 1] = c
    pixels[x - 2, y + 0] = c
    pixels[x + 1, y + 0] = c
    pixels[x + 2, y + 0] = c
    pixels[x - 2, y + 1] = c
    pixels[x + 2, y + 1] = c
    pixels[x - 3, y + 2] = c
    pixels[x - 1, y + 2] = c
    pixels[x + 3, y + 2] = c
    pixels[x - 3, y + 3] = c
    pixels[x - 2, y + 3] = c
    pixels[x - 1, y + 3] = c
    pixels[x - 0, y + 3] = c
    pixels[x + 1, y + 3] = c
    pixels[x + 2, y + 3] = c
    pixels[x + 3, y + 3] = c
    pixels[x - 0, y + 4] = c

    pixels[x + 0, y - 2] = c2
    pixels[x + 0, y - 1] = c2
    pixels[x - 1, y - 0] = c2
    pixels[x - 0, y - 0] = c2
    pixels[x - 1, y + 1] = c2
    pixels[x - 0, y + 1] = c2
    pixels[x + 1, y + 1] = c2
    pixels[x - 2, y + 2] = c2
    pixels[x - 0, y + 2] = c2
    pixels[x + 1, y + 2] = c2
    pixels[x + 2, y + 2] = c2

def draw_temperate_forest2(pixels, x, y, w, h):
    c = (0, 64, 0, 255)
    c2 = (0, 112, 0, 255)
    pixels[x - 1, y - 4] = c
    pixels[x - 0, y - 4] = c
    pixels[x + 1, y - 4] = c
    pixels[x - 2, y - 3] = c
    pixels[x - 1, y - 3] = c
    pixels[x + 2, y - 3] = c
    pixels[x - 2, y - 2] = c
    pixels[x + 1, y - 2] = c
    pixels[x + 2, y - 2] = c
    pixels[x - 2, y - 1] = c
    pixels[x + 2, y - 1] = c
    pixels[x - 2, y - 0] = c
    pixels[x - 1, y - 0] = c
    pixels[x + 2, y - 0] = c
    pixels[x - 2, y + 1] = c
    pixels[x + 1, y + 1] = c
    pixels[x + 2, y + 1] = c
    pixels[x - 1, y + 2] = c
    pixels[x - 0, y + 2] = c
    pixels[x + 1, y + 2] = c
    pixels[x - 0, y + 3] = c
    pixels[x - 0, y + 4] = c

    pixels[x + 0, y - 3] = c2
    pixels[x + 1, y - 3] = c2
    pixels[x - 1, y - 2] = c2
    pixels[x - 0, y - 2] = c2
    pixels[x - 1, y - 1] = c2
    pixels[x - 0, y - 1] = c2
    pixels[x + 1, y - 1] = c2
    pixels[x - 0, y - 0] = c2
    pixels[x + 1, y - 0] = c2
    pixels[x - 1, y + 1] = c2
    pixels[x - 0, y + 1] = c2

def draw_steppe(pixels, x, y):
    b = (x ** int(y / 5) + x * 23 + y * 37 + (x * y) * 13) % 75
    r = 96 - b
    g = 192 - b
    b = 96 - b
    pixels[x, y] = (r, g, b, 255)

def draw_cool_desert(pixels, x, y, w, h):
    c = (72, 72, 53, 255)
    c2 = (219, 220, 200, 255)

    pixels[x - 1, y - 2] = c
    pixels[x - 0, y - 2] = c
    pixels[x + 1, y - 2] = c
    pixels[x + 1, y - 2] = c
    pixels[x + 2, y - 2] = c
    pixels[x - 2, y - 1] = c
    pixels[x - 1, y - 1] = c
    pixels[x - 0, y - 1] = c
    pixels[x + 4, y - 1] = c
    pixels[x - 4, y - 0] = c
    pixels[x - 3, y - 0] = c
    pixels[x - 2, y - 0] = c
    pixels[x - 1, y - 0] = c
    pixels[x + 1, y - 0] = c
    pixels[x + 2, y - 0] = c
    pixels[x + 6, y - 0] = c
    pixels[x - 5, y + 1] = c
    pixels[x - 0, y + 1] = c
    pixels[x + 7, y + 1] = c
    pixels[x + 8, y + 1] = c
    pixels[x - 8, y + 2] = c
    pixels[x - 7, y + 2] = c

def draw_warm_temperate_forest(pixels, x, y, w, h):
    c = (0, 96, 0, 255)
    c2 = (0, 192, 0, 255)
    pixels[x - 1, y - 4] = c
    pixels[x - 0, y - 4] = c
    pixels[x + 1, y - 4] = c
    pixels[x - 2, y - 3] = c
    pixels[x - 1, y - 3] = c
    pixels[x + 2, y - 3] = c
    pixels[x - 2, y - 2] = c
    pixels[x + 1, y - 2] = c
    pixels[x + 2, y - 2] = c
    pixels[x - 2, y - 1] = c
    pixels[x + 2, y - 1] = c
    pixels[x - 2, y - 0] = c
    pixels[x - 1, y - 0] = c
    pixels[x + 2, y - 0] = c
    pixels[x - 2, y + 1] = c
    pixels[x + 1, y + 1] = c
    pixels[x + 2, y + 1] = c
    pixels[x - 1, y + 2] = c
    pixels[x - 0, y + 2] = c
    pixels[x + 1, y + 2] = c
    pixels[x - 0, y + 3] = c
    pixels[x - 0, y + 4] = c

    pixels[x + 0, y - 3] = c2
    pixels[x + 1, y - 3] = c2
    pixels[x - 1, y - 2] = c2
    pixels[x - 0, y - 2] = c2
    pixels[x - 1, y - 1] = c2
    pixels[x - 0, y - 1] = c2
    pixels[x + 1, y - 1] = c2
    pixels[x - 0, y - 0] = c2
    pixels[x + 1, y - 0] = c2
    pixels[x - 1, y + 1] = c2
    pixels[x - 0, y + 1] = c2

def draw_chaparral(pixels, x, y):
    b = (x ** int(y / 5) + x * 23 + y * 37 + (x * y) * 13) % 75
    r = 180 - b
    g = 171 - b
    b = 113 - b
    pixels[x, y] = (r, g, b, 255)

def draw_hot_desert(pixels, x, y, w, h):
    c = (72, 72, 53, 255)
    c2 = (219, 220, 200, 255)

    pixels[x - 1, y - 2] = c
    pixels[x - 0, y - 2] = c
    pixels[x + 1, y - 2] = c
    pixels[x + 1, y - 2] = c
    pixels[x + 2, y - 2] = c
    pixels[x - 2, y - 1] = c
    pixels[x - 1, y - 1] = c
    pixels[x - 0, y - 1] = c
    pixels[x + 4, y - 1] = c
    pixels[x - 4, y - 0] = c
    pixels[x - 3, y - 0] = c
    pixels[x - 2, y - 0] = c
    pixels[x - 1, y - 0] = c
    pixels[x + 1, y - 0] = c
    pixels[x + 2, y - 0] = c
    pixels[x + 6, y - 0] = c
    pixels[x - 5, y + 1] = c
    pixels[x - 0, y + 1] = c
    pixels[x + 7, y + 1] = c
    pixels[x + 8, y + 1] = c
    pixels[x - 8, y + 2] = c
    pixels[x - 7, y + 2] = c

def draw_temperate_forest(pixels, x, y, w, h):
    c = (0, 128, 0, 255)
    c2 = (0, 192, 0, 255)
    pixels[x + 0, y - 3] = c
    pixels[x - 1, y - 2] = c
    pixels[x + 1, y - 2] = c
    pixels[x - 2, y - 1] = c
    pixels[x + 2, y - 1] = c
    pixels[x - 2, y + 0] = c
    pixels[x + 2, y + 0] = c
    pixels[x - 1, y + 1] = c
    pixels[x + 0, y + 1] = c
    pixels[x + 1, y + 1] = c
    pixels[x + 0, y + 2] = c
    pixels[x + 0, y + 2] = c

    pixels[x + 0, y - 2] = c2
    pixels[x - 1, y - 1] = c2
    pixels[x + 0, y - 1] = c2
    pixels[x + 1, y - 1] = c2
    pixels[x - 1, y - 0] = c2
    pixels[x + 0, y - 0] = c2
    pixels[x + 1, y - 0] = c2

def draw_tropical_dry_forest(pixels, x, y, w, h):
    c = (51, 36, 3, 255)
    c2 = (139, 204, 58, 255)
    pixels[x - 1, y - 4] = c
    pixels[x - 0, y - 4] = c
    pixels[x + 1, y - 4] = c
    pixels[x - 2, y - 3] = c
    pixels[x - 1, y - 3] = c
    pixels[x + 2, y - 3] = c
    pixels[x - 2, y - 2] = c
    pixels[x + 1, y - 2] = c
    pixels[x + 2, y - 2] = c
    pixels[x - 2, y - 1] = c
    pixels[x + 2, y - 1] = c
    pixels[x - 2, y - 0] = c
    pixels[x - 1, y - 0] = c
    pixels[x + 2, y - 0] = c
    pixels[x - 2, y + 1] = c
    pixels[x + 1, y + 1] = c
    pixels[x + 2, y + 1] = c
    pixels[x - 1, y + 2] = c
    pixels[x - 0, y + 2] = c
    pixels[x + 1, y + 2] = c
    pixels[x - 0, y + 3] = c
    pixels[x - 0, y + 4] = c

    pixels[x + 0, y - 3] = c2
    pixels[x + 1, y - 3] = c2
    pixels[x - 1, y - 2] = c2
    pixels[x - 0, y - 2] = c2
    pixels[x - 1, y - 1] = c2
    pixels[x - 0, y - 1] = c2
    pixels[x + 1, y - 1] = c2
    pixels[x - 0, y - 0] = c2
    pixels[x + 1, y - 0] = c2
    pixels[x - 1, y + 1] = c2
    pixels[x - 0, y + 1] = c2

def draw_jungle(pixels, x, y, w, h):
    c = (0, 128, 0, 255)
    c2 = (0, 255, 0, 255)
    pixels[x - 1, y - 4] = c
    pixels[x - 0, y - 4] = c
    pixels[x + 1, y - 4] = c
    pixels[x - 2, y - 3] = c
    pixels[x - 1, y - 3] = c
    pixels[x + 2, y - 3] = c
    pixels[x - 2, y - 2] = c
    pixels[x + 1, y - 2] = c
    pixels[x + 2, y - 2] = c
    pixels[x - 2, y - 1] = c
    pixels[x + 2, y - 1] = c
    pixels[x - 2, y - 0] = c
    pixels[x - 1, y - 0] = c
    pixels[x + 2, y - 0] = c
    pixels[x - 2, y + 1] = c
    pixels[x + 1, y + 1] = c
    pixels[x + 2, y + 1] = c
    pixels[x - 1, y + 2] = c
    pixels[x - 0, y + 2] = c
    pixels[x + 1, y + 2] = c
    pixels[x - 0, y + 3] = c
    pixels[x - 0, y + 4] = c

    pixels[x + 0, y - 3] = c2
    pixels[x + 1, y - 3] = c2
    pixels[x - 1, y - 2] = c2
    pixels[x - 0, y - 2] = c2
    pixels[x - 1, y - 1] = c2
    pixels[x - 0, y - 1] = c2
    pixels[x + 1, y - 1] = c2
    pixels[x - 0, y - 0] = c2
    pixels[x + 1, y - 0] = c2
    pixels[x - 1, y + 1] = c2
    pixels[x - 0, y + 1] = c2


def draw_savanna(pixels, x, y):
    b = (x ** int(y / 5) + x * 23 + y * 37 + (x * y) * 13) % 75
    r = 255 - b
    g = 246 - b
    b = 188 - b
    pixels[x, y] = (r, g, b, 255)

def draw_a_mountain(pixels, x, y, w=3, h=3):
    mcl = (0, 0, 0, 255)
    mcll = (128, 128, 128, 255)
    mcr = (75, 75, 75, 255)
    # left edge
    for mody in range(-h, h + 1):
        bottomness = (float(mody + h) / 2.0) / w
        leftborder = int(bottomness * w)
        darkarea = int(bottomness * w / 2)
        lightarea = int(bottomness * w / 2)
        for itx in range(darkarea, leftborder + 1):
            pixels[x - itx, y + mody] = gradient(itx, darkarea, leftborder, (0, 0, 0), (64, 64, 64))
        for itx in range(-darkarea, lightarea + 1):
            pixels[x + itx, y + mody] = gradient(itx, -darkarea, lightarea, (64, 64, 64), (128, 128, 128))
        for itx in range(lightarea, leftborder):
            pixels[x + itx, y + mody] = (181, 166, 127, 255)  # land_color
    # right edge
    for mody in range(-h, h + 1):
        bottomness = (float(mody + h) / 2.0) / w
        modx = int(bottomness * w)
        pixels[x + modx, y + mody] = mcr

def pseudo_random_land_pos(world, i):
    y = (i ** 7 + i * 23) % world.height
    x = (i ** 13 + i * 37) % world.width
    if world.is_land((x, y)):
        return (int(x), int(y))
    else:
        return pseudo_random_land_pos(world, (i % 123456789) * 17 + 11)


def draw_oldmap_on_pixels(world, pixels, factor=1, sea_color=(212, 198, 169, 255), verbose=True):
    # TODO use global verbose
    if verbose:
        start_time = time.time()

    land_color = (181, 166, 127, 255)           # TODO: Put this in the argument list too??
    borders = find_land_borders(world, factor)
    mountains_mask = find_mountains_mask(world, factor)
    boreal_forest_mask = find_boreal_forest_mask(world, factor)
    temperate_forest_mask = find_temperate_forest_mask(world, factor)
    warm_temperate_forest_mask = find_warm_temperate_forest_mask(world, factor)
    tropical_dry_forest_mask = find_tropical_dry_forest_mask(world, factor)
    jungle_mask = mask(world, world.is_jungle, factor) #jungle is actually Tropical Rain Forest and Tropical Seasonal Forest
    tundra_mask = mask(world, world.is_tundra, factor)
    savanna_mask = mask(world, world.is_savanna, factor) #savanna is actually Tropical semi-arid
    cold_parklands_mask = mask(world, world.is_cold_parklands, factor)
    steppe_mask = mask(world, world.is_steppe, factor)
    cool_desert_mask = mask(world, world.is_cool_desert, factor)
    chaparral_mask = mask(world, world.is_chaparral, factor)
    hot_desert_mask = mask(world, world.is_hot_desert, factor)

    def unset_mask(pos):
        x, y = pos
        mountains_mask[y][x] = False

    def unset_boreal_forest_mask(pos):
        x, y = pos
        boreal_forest_mask[y][x] = False

    def unset_temperate_forest_mask(pos):
        x, y = pos
        temperate_forest_mask[y][x] = False

    def unset_warm_temperate_forest_mask(pos):
        x, y = pos
        warm_temperate_forest_mask[y][x] = False

    def unset_tropical_dry_forest_mask(pos):
        x, y = pos
        tropical_dry_forest_mask[y][x] = False

    def unset_jungle_mask(pos):
        x, y = pos
        jungle_mask[y][x] = False

    def unset_tundra_mask(pos):
        x, y = pos
        tundra_mask[y][x] = False

    def unset_savanna_mask(pos):
        x, y = pos
        savanna_mask[y][x] = False

    def unset_hot_desert_mask(pos):
        x, y = pos
        hot_desert_mask[y][x] = False

    def unset_rock_desert_mask(pos):
        x, y = pos
        rock_desert_mask[y][x] = False

    def unset_cold_parklands_mask(pos):
        x, y = pos
        cold_parklands_mask[y][x] = False

    def unset_steppe_mask(pos):
        x, y = pos
        steppe_mask[y][x] = False

    def unset_cool_desert_mask(pos):
        x, y = pos
        cool_desert_mask[y][x] = False

    def unset_chaparral_mask(pos):
        x, y = pos
        chaparral_mask[y][x] = False

    def on_border(pos):
        x, y = pos
        return borders[y][x]
    if verbose:
        elapsed_time = time.time() - start_time
        print("...drawing_functions.draw_oldmap_on_pixel: init Elapsed time " + str(elapsed_time) + " seconds.")
        sys.stdout.flush()

    if verbose:
        start_time = time.time()
    min_elev = None
    max_elev = None
    for y in xrange(world.height):
        for x in xrange(world.width):
            e = world.elevation['data'][y][x]
            if min_elev is None or e < min_elev:
                min_elev = e
            if max_elev is None or e > max_elev:
                max_elev = e
    elev_delta = max_elev - min_elev
    if verbose:
        elapsed_time = time.time() - start_time
        print("...drawing_functions.draw_oldmap_on_pixel: max, min elevation Elapsed time " + str(elapsed_time) +"  seconds.")

    if verbose:
        start_time = time.time()
    for y in xrange(factor*world.height):
        for x in xrange(factor*world.width):
            xf = int(x/factor)
            yf = int(y/factor)
            if borders[y][x]:
                pixels[x, y] = (0, 0, 0, 255)
            elif world.ocean[yf][xf]:
                pixels[x, y] = sea_color
            else:
                pixels[x, y] = land_color
    if verbose:
        elapsed_time = time.time() - start_time
        print("...drawing_functions.draw_oldmap_on_pixel: color ocean Elapsed time " +str(elapsed_time) +" seconds.")

    if verbose:
        start_time = time.time()
    def antialias(steps):

        def _antialias_step():
            for y in xrange(factor*world.height):
                for x in xrange(factor*world.width):
                    _antialias_point(x, y)

        def _antialias_point(x, y):
            n = 2
            tot_r = pixels[x, y][0] * 2
            tot_g = pixels[x, y][1] * 2
            tot_b = pixels[x, y][2] * 2
            for dy in range(-1, +2):
                py = y + dy
                if py > 0 and py < factor*world.height:
                    for dx in range(-1, +2):
                        px = x + dx
                        if px > 0 and px < factor*world.width:
                            n += 1
                            tot_r += pixels[px, py][0]
                            tot_g += pixels[px, py][1]
                            tot_b += pixels[px, py][2]
            r = int(tot_r/n)
            g = int(tot_g/n)
            b = int(tot_b/n)
            pixels[x, y] = (r,g,b,255)

        for i in range(0, steps):
            _antialias_step()

    antialias(1)
    if verbose:
        elapsed_time = time.time() - start_time
        print("...drawing_functions.draw_oldmap_on_pixel: anti alias Elapsed time " +str(elapsed_time) +" seconds.")

    # Draw glacier
    if verbose:
        start_time = time.time()
    for y in xrange(factor*world.height):
        for x in xrange(factor*world.width):
            if not borders[y][x] and world.is_iceland((int(x/factor), int(y/factor))):
                draw_glacier(pixels, x, y)
    if verbose:
        elapsed_time = time.time() - start_time
        print("...drawing_functions.draw_oldmap_on_pixel: draw glacier Elapsed time " +str(elapsed_time) +" seconds.")

    # Draw tundra
    if verbose:
        start_time = time.time()
    for y in xrange(factor*world.height):
        for x in xrange(factor*world.width):
            if tundra_mask[y][x]:
                draw_tundra(pixels, x, y)
    if verbose:
        elapsed_time = time.time() - start_time
        print("...drawing_functions.draw_oldmap_on_pixel: draw tundra Elapsed time " +str(elapsed_time) +" seconds.")

    # Draw cold parklands
    for y in xrange(factor*world.height):
        for x in xrange(factor*world.width):
            if cold_parklands_mask[y][x]:
                draw_cold_parklands(pixels, x, y)

    # Draw steppes
    for y in xrange(factor*world.height):
        for x in xrange(factor*world.width):
            if steppe_mask[y][x]:
                draw_steppe(pixels, x, y)

    # Draw chaparral
    for y in xrange(factor*world.height):
        for x in xrange(factor*world.width):
            if chaparral_mask[y][x]:
                draw_chaparral(pixels, x, y)

    # Draw savanna
    for y in xrange(factor*world.height):
        for x in xrange(factor*world.width):
            if savanna_mask[y][x]:
                draw_savanna(pixels, x, y)

    # Draw cool desert
    for y in xrange(factor*world.height):
        for x in xrange(factor*world.width):
            if cool_desert_mask[y][x]:
                w = 8
                h = 2
                r = 9
                if len(world.tiles_around_factor(factor, (x, y), radius=r, predicate=on_border)) <= 2:
                    draw_cool_desert(pixels, x, y, w=w, h=h)
                    world.on_tiles_around_factor(factor, (x, y), radius=r, action=unset_cool_desert_mask)

    # Draw hot desert
    for y in xrange(factor*world.height):
        for x in xrange(factor*world.width):
            if hot_desert_mask[y][x]:
                w = 8
                h = 2
                r = 9
                if len(world.tiles_around_factor(factor, (x, y), radius=r, predicate=on_border)) <= 2:
                    draw_hot_desert(pixels, x, y, w=w, h=h)
                    world.on_tiles_around_factor(factor, (x, y), radius=r, action=unset_hot_desert_mask)

    # Draw boreal forest
    for y in xrange(factor*world.height):
        for x in xrange(factor*world.width):
            if boreal_forest_mask[y][x]:
                w = 4
                h = 5
                r = 6
                if len(world.tiles_around_factor(factor, (x, y), radius=r, predicate=on_border)) <= 2:
                    draw_boreal_forest(pixels, x, y, w=w, h=h)
                    world.on_tiles_around_factor(factor, (x, y), radius=r, action=unset_boreal_forest_mask)

    # Draw temperate forest
    for y in xrange(factor*world.height):
        for x in xrange(factor*world.width):
            if temperate_forest_mask[y][x]:
                w = 4
                h = 5
                r = 6
                if len(world.tiles_around_factor(factor, (x, y), radius=r, predicate=on_border)) <= 2:
                    if random.random() <= .5:
                        draw_temperate_forest1(pixels, x, y, w=w, h=h)
                    else:
                        draw_temperate_forest2(pixels, x, y, w=w, h=h)
                    world.on_tiles_around_factor(factor, (x, y), radius=r, action=unset_temperate_forest_mask)

    # Draw warm temperate forest
    for y in xrange(factor*world.height):
        for x in xrange(factor*world.width):
            if warm_temperate_forest_mask[y][x]:
                w = 4
                h = 5
                r = 6
                if len(world.tiles_around_factor(factor, (x, y), radius=r, predicate=on_border)) <= 2:
                    draw_warm_temperate_forest(pixels, x, y, w=w, h=h)
                    world.on_tiles_around_factor(factor, (x, y), radius=r, action=unset_warm_temperate_forest_mask)

    # Draw dry tropical forest
    for y in xrange(factor*world.height):
        for x in xrange(factor*world.width):
            if tropical_dry_forest_mask[y][x]:
                w = 4
                h = 5
                r = 6
                if len(world.tiles_around_factor(factor, (x, y), radius=r, predicate=on_border)) <= 2:
                    draw_tropical_dry_forest(pixels, x, y, w=w, h=h)
                    world.on_tiles_around_factor(factor, (x, y), radius=r, action=unset_tropical_dry_forest_mask)

    # Draw jungle
    for y in xrange(factor*world.height):
        for x in xrange(factor*world.width):
            if jungle_mask[y][x]:
                w = 4
                h = 5
                r = 6
                if len(world.tiles_around_factor(factor, (x, y), radius=r, predicate=on_border)) <= 2:
                    draw_jungle(pixels, x, y, w=w, h=h)
                    world.on_tiles_around_factor(factor, (x, y), radius=r, action=unset_jungle_mask)

    draw_riversmap_on_image(world, pixels, factor)

    # Draw mountains
    if verbose:
        start_time = time.time()
    for y in xrange(factor*world.height):
        for x in xrange(factor*world.width):
            if mountains_mask[y][x]:
                w = mountains_mask[y][x]
                h = 3 + int(world.level_of_mountain((int(x/factor), int(y/factor))))
                r = max(int(w / 3 * 2), h)
                if len(world.tiles_around_factor(factor, (x, y), radius=r, predicate=on_border)) <= 2:
                    draw_a_mountain(pixels, x, y, w=w, h=h)
                    world.on_tiles_around_factor(factor, (x, y), radius=r, action=unset_mask)
    if verbose:
        elapsed_time = time.time() - start_time
        print("...drawing_functions.draw_oldmap_on_pixel: draw mountains Elapsed time " +str(elapsed_time) +" seconds.")


    return pixels


def draw_riversmap_on_image(world, pixels, factor=1):
    n_rivers = int(math.sqrt(world.width * world.height))
    for i in range(1, n_rivers):
        candidates = []
        for j in range(1, 10):
            candidates.append(pseudo_random_land_pos(world, i * j + j))
        max = None
        cc = None
        for c in candidates:
            cx, cy = c
            wl = world.humidity['data'][cy][cx] * world.precipitation['data'][cy][cx] * world.elevation['data'][cy][cx]
            if max is None or wl > max:
                max = wl
                cc = c
        draw_river(world, pixels, cc, factor)


def draw_river(world, pixels, pos, factor):
    if world.is_ocean(pos):
        return
    x, y = pos
    for dx in xrange(factor):
        for dy in xrange(factor):
            pixels[x*factor+dx, y*factor+dy] = (0, 0, 128, 255)
    draw_river(world, pixels, lowest_neighbour(world, pos), factor)


def lowest_neighbour(world, pos):
    x, y = pos
    lowest = None
    lowest_lvl = None
    for dx in xrange(-1, 1):
        for dy in xrange(-1, 1):
            if dx != 0 or dy != 0:
                e = world.elevation['data'][y + dy][x + dx]  # +world.humidity['data'][y+dy][x+dx]/3.0
                if (not lowest_lvl) or (e < lowest_lvl):
                    lowest_lvl = e
                    lowest = (x + dx, y + dy)
                elif (e == lowest_lvl) and ((x + y + dx + dy) % 2 == 0):
                    lowest_lvl = e
                    lowest = (x + dx, y + dy)

    return lowest
