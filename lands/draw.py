__author__ = 'Federico Tomassetti'

from PIL import Image

from lands.drawing_functions import *

import sys
if sys.version_info > (2,):
    xrange = range


def draw_land_profile(elevation, sea_level, filename):
    WIDTH = len(elevation[0])
    HEIGHT = len(elevation)

    img = Image.new('RGBA', (WIDTH, HEIGHT))
    pixels = img.load()
    for y in range(0, HEIGHT):
        for x in range(0, WIDTH):
            if elevation[y][x] > sea_level:
                pixels[x, y] = (0, 255, 0, 255)
            else:
                pixels[x, y] = (0, 0, 255, 255)
    img.save(filename)


def elevation_color(c, color_step = 1.5):
    COLOR_STEP = color_step
    if c < 0.5:
        return (0.0, 0.0, 0.25 + 1.5 * c)
    elif c < 1.0:
        return (0.0, 2 * (c - 0.5), 1.0)
    else:
        c -= 1.0;
        if c < 1.0 * COLOR_STEP:
            return (0.0, 0.5 +
                    0.5 * c / COLOR_STEP, 0.0)
        elif (c < 1.5 * COLOR_STEP):
            return (2 * (c - 1.0 * COLOR_STEP) / COLOR_STEP, 1.0, 0.0)
        elif (c < 2.0 * COLOR_STEP):
            return (1.0, 1.0 - (c - 1.5 * COLOR_STEP) / COLOR_STEP, 0)
        elif (c < 3.0 * COLOR_STEP):
            return (1.0 - 0.5 * (c - 2.0 *
                                 COLOR_STEP) / COLOR_STEP,
                    0.5 - 0.25 * (c - 2.0 *
                                  COLOR_STEP) / COLOR_STEP, 0)
        elif (c < 5.0 * COLOR_STEP):
            return (0.5 - 0.125 * (c - 3.0 *
                                   COLOR_STEP) / (2 * COLOR_STEP),
                    0.25 + 0.125 * (c - 3.0 *
                                    COLOR_STEP) / (2 * COLOR_STEP),
                    0.375 * (c - 3.0 *
                             COLOR_STEP) / (2 * COLOR_STEP))
        elif (c < 8.0 * COLOR_STEP):
            return (0.375 + 0.625 * (c - 5.0 *
                                     COLOR_STEP) / (3 * COLOR_STEP),
                    0.375 + 0.625 * (c - 5.0 *
                                     COLOR_STEP) / (3 * COLOR_STEP),
                    0.375 + 0.625 * (c - 5.0 *
                                     COLOR_STEP) / (3 * COLOR_STEP))
        else:
            c -= 8.0 * COLOR_STEP
            while (c > 2.0 * COLOR_STEP):
                c -= 2.0 * COLOR_STEP
            return (1, 1 - c / 4.0, 1)    

def draw_simple_elevation_on_image(data, shadow, width, height):    
    img = Image.new('RGBA', (width, height))
    pixels = img.load()

    for y in range(0, height):
        for x in range(0, width):
            e = data[y * width + x]
            r, g, b = elevation_color(e)
            pixels[x, y] = (int(r * 255), int(g * 255), int(b * 255), 255)
    return img

def draw_simple_elevation(data, filename, shadow, width, height):
    img = draw_simple_elevation_on_image(data, shadow, width, height)
    img.save(filename)


def generate_riversmap(world_path, map_path):
    import pickle

    with open(world_path, 'r') as f:
        w = pickle.load(f)

    # Generate images
    draw_riversmap(w, map_path)


def draw_riversmap(world, filename):
    img = Image.new('RGBA', (world.width, world.height))
    pixels = img.load()

    sea_color = (255, 255, 255, 255)
    land_color = (0, 0, 0, 255)

    for y in xrange(world.height):
        for x in xrange(world.width):
            if world.ocean[y][x]:
                pixels[x, y] = sea_color
            else:
                pixels[x, y] = land_color

    draw_riversmap_on_image(world, pixels, 1)

    img.save(filename)


def draw_grayscale_heightmap(world, filename):
    img = Image.new('RGBA', (world.width, world.height))
    pixels = img.load()

    min_elev_sea = None
    max_elev_sea = None
    min_elev_land = None
    max_elev_land = None
    for y in xrange(world.height):
        for x in xrange(world.width):
            e = world.elevation['data'][y][x]
            if world.is_land((x,y)):
                if min_elev_land is None or e < min_elev_land:
                    min_elev_land = e
                if max_elev_land is None or e > max_elev_land:
                    max_elev_land = e
            else:
                if min_elev_sea is None or e < min_elev_sea:
                    min_elev_sea = e
                if max_elev_sea is None or e > max_elev_sea:
                    max_elev_sea = e

    elev_delta_land = max_elev_land - min_elev_land
    elev_delta_sea = max_elev_sea - min_elev_sea

    for y in xrange(world.height):
        for x in xrange(world.width):
            e = world.elevation['data'][y][x]
            if world.is_land((x,y)):
                c = int(((e - min_elev_land) * 127) / elev_delta_land)+128
            else:
                c = int(((e - min_elev_sea) * 127) / elev_delta_sea)
            pixels[x, y] = (c, c, c, 255)
    img.save(filename)


def draw_bw_heightmap_for_a_biome(world, filename, biome):
    img = Image.new('RGBA', (world.width, world.height))
    pixels = img.load()

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

    for y in xrange(world.height):
        for x in xrange(world.width):
            e = world.elevation['data'][y][x]
            c = int(((e - min_elev) * 255) / elev_delta)
            if not world.biome[y][x] == biome:
                a = 0
            else:
                a = 255
            pixels[x, y] = (c, c, c, a)
    img.save(filename)


def draw_elevation(world, filename, shadow=True):
    WIDTH = world.width
    HEIGHT = world.height

    data = world.elevation['data']
    ocean = world.ocean
    img = Image.new('RGBA', (WIDTH, HEIGHT))
    pixels = img.load()

    min_elev = None
    max_elev = None
    for y in xrange(HEIGHT):
        for x in xrange(WIDTH):
            if not ocean[y][x]:
                e = data[y][x]
                if min_elev is None or e < min_elev:
                    min_elev = e
                if max_elev is None or e > max_elev:
                    max_elev = e
    elev_delta = max_elev - min_elev

    for y in range(0, HEIGHT):
        for x in range(0, WIDTH):
            if ocean[y][x]:
                pixels[x, y] = (0, 0, 255, 255)
            else:
                e = data[y][x]
                c = 255 - int(((e - min_elev) * 255) / elev_delta)
                if shadow and y > 2 and x > 2:
                    if data[y - 1][x - 1] > e:
                        c -= 15
                    if data[y - 2][x - 2] > e and data[y - 2][x - 2] > data[y - 1][x - 1]:
                        c -= 10
                    if data[y - 3][x - 3] > e and data[y - 3][x - 3] > data[y - 1][x - 1] and data[y - 3][x - 3] > \
                            data[y - 2][x - 2]:
                        c -= 5
                    if c < 0:
                        c = 0
                pixels[x, y] = (c, c, c, 255)
    img.save(filename)


def draw_irrigation(world, filename):
    WIDTH = world.width
    HEIGHT = world.height

    data = world.irrigation
    ocean = world.ocean
    img = Image.new('RGBA', (WIDTH, HEIGHT))
    pixels = img.load()

    min_elev = None
    max_elev = None
    for y in xrange(HEIGHT):
        for x in xrange(WIDTH):
            if not ocean[y][x]:
                e = data[y][x]
                if min_elev is None or e < min_elev:
                    min_elev = e
                if max_elev is None or e > max_elev:
                    max_elev = e
    elev_delta = max_elev - min_elev

    for y in range(0, HEIGHT):
        for x in range(0, WIDTH):
            if ocean[y][x]:
                pixels[x, y] = (0, 0, 255, 255)
            else:
                e = data[y][x]
                c = int(((e - min_elev) * 255) / elev_delta)
                pixels[x, y] = (0, 0, c, 255)
    img.save(filename)


def draw_humidity(world, filename):
    WIDTH = world.width
    HEIGHT = world.height

    ocean = world.ocean
    img = Image.new('RGBA', (WIDTH, HEIGHT))
    pixels = img.load()

    min_elev = None
    max_elev = None
    for y in xrange(HEIGHT):
        for x in xrange(WIDTH):
            if not ocean[y][x]:
                e = world.humidity['data'][y][x]
                if min_elev is None or e < min_elev:
                    min_elev = e
                if max_elev is None or e > max_elev:
                    max_elev = e
    elev_middle = world.humidity['quantiles']['50']
    elev_delta_plus = max_elev - elev_middle
    elev_delta_minus = elev_middle - min_elev

    for y in range(0, HEIGHT):
        for x in range(0, WIDTH):
            if ocean[y][x]:
                pixels[x, y] = (0, 0, 255, 255)
            else:
                e = world.humidity['data'][y][x]
                if e < elev_middle:
                    c = int(((elev_middle - e) * 255) / elev_delta_minus)
                    pixels[x, y] = (c, 0, 0, 255)
                else:
                    c = int(((e - elev_middle) * 255) / elev_delta_plus)
                    pixels[x, y] = (0, c, 0, 255)

    img.save(filename)


def draw_watermap(world, filename, th):
    # TODO use WatermapView
    WIDTH = world.width
    HEIGHT = world.height

    ocean = world.ocean
    img = Image.new('RGBA', (WIDTH, HEIGHT))
    pixels = img.load()

    # min_elev = None 	
    # max_elev = None 	
    # for y in xrange(HEIGHT): 	
    # for x in xrange(WIDTH): 	
    # if not ocean[y][x]: 	
    # e = _watermap[y][x]**1.5 	
    # if min_elev==None or e<min_elev: 	
    # min_elev=e 	
    # if max_elev==None or e>max_elev: 	
    # max_elev=e 	
    # elev_delta = max_elev-min_elev 	
    # if elev_delta<1: 	
    # elev_delta=1 	

    for y in range(0, HEIGHT):
        for x in range(0, WIDTH):
            if ocean[y][x]:
                pixels[x, y] = (0, 0, 255, 255)
            else:
                e = world.watermap[y][x]
                if e > th:
                    c = 255
                else:
                    c = 0
                    #c = int(((e-min_elev)*255)/elev_delta)
                pixels[x, y] = (c, 0, 0, 255)
    img.save(filename)


def draw_land(elevation, ocean_map, hill_level, mountain_level, filename):
    WIDTH = len(elevation[0])
    HEIGHT = len(elevation)

    img = Image.new('RGBA', (WIDTH, HEIGHT))
    pixels = img.load()
    for y in range(0, HEIGHT):
        for x in range(0, WIDTH):
            if ocean_map[y][x]:
                pixels[x, y] = (0, 0, 255, 255)
            elif elevation[y][x] > mountain_level:
                pixels[x, y] = (255, 255, 255, 255)
            elif elevation[y][x] > hill_level:
                pixels[x, y] = (30, 140, 30, 255)
            else:
                pixels[x, y] = (0, 230, 0, 255)

    img.save(filename)


def draw_ocean(ocean, filename):
    WIDTH = len(ocean[0])
    HEIGHT = len(ocean)

    img = Image.new('RGBA', (WIDTH, HEIGHT))
    pixels = img.load()
    for y in range(0, HEIGHT):
        for x in range(0, WIDTH):
            if ocean[y][x]:
                pixels[x, y] = (0, 0, 255, 255)
            else:
                pixels[x, y] = (0, 255, 255, 255)
    img.save(filename)


def draw_temp(temp, filename):
    WIDTH = len(temp[0])
    HEIGHT = len(temp)

    img = Image.new('RGBA', (WIDTH, HEIGHT))
    pixels = img.load()
    for y in range(0, HEIGHT):
        for x in range(0, WIDTH):
            c = int(temp[y][x] * 255)
            pixels[x, y] = (c, 0, 0, 255)
    img.save(filename)


def draw_precipitation(world, filename):
    # FIXME we are drawing humidity, not precipitations
    WIDTH = world.width
    HEIGHT = world.height

    img = Image.new('RGBA', (WIDTH, HEIGHT))
    pixels = img.load()
    for y in range(0, HEIGHT):
        for x in range(0, WIDTH):
            if world.is_humidity_superarid((x, y)):
                pixels[x, y] = (0, 32, 32, 255)
            elif world.is_humidity_perarid((x, y)):
                pixels[x, y] = (0, 64, 64, 255)
            elif world.is_humidity_arid((x, y)):
                pixels[x, y] = (0, 96, 96, 255)
            elif world.is_humidity_semiarid((x, y)):
                pixels[x, y] = (0, 128, 128, 255)
            elif world.is_humidity_subhumid((x, y)):
                pixels[x, y] = (0, 160, 160, 255)
            elif world.is_humidity_humid((x, y)):
                pixels[x, y] = (0, 192, 192, 255)
            elif world.is_humidity_perhumid((x, y)):
                pixels[x, y] = (0, 224, 224, 255)
            elif world.is_humidity_superhumid((x, y)):
                pixels[x, y] = (0, 255, 255, 255)
    img.save(filename)


def draw_sea(world, filename):
    WIDTH = world.width
    HEIGHT = world.height

    img = Image.new('RGBA', (WIDTH, HEIGHT))

    pixels = img.load()
    for y in range(0, HEIGHT):
        for x in range(0, WIDTH):
            if world.is_land((x, y)):
                pixels[x, y] = (255, 255, 255, 255)
            else:
                c = int(world.sea_depth[y][x] * 200 + 50)
                pixels[x, y] = (0, 0, 255 - c, 255)
    img.save(filename)


class Counter(object):

    def __init__(self):
        self.c = {}

    def count(self, what):
        if what not in self.c:
            self.c[what] = 0
        self.c[what] += 1

    def printself(self):
        for w in self.c.keys():
            print("%s : %i" % (w, self.c[w]))

def draw_world(world, filename):
    WIDTH = world.width
    HEIGHT = world.height

    img = Image.new('RGBA', (WIDTH, HEIGHT))

    counter = Counter()

    pixels = img.load()
    for y in range(0, HEIGHT):
        for x in range(0, WIDTH):
            if world.is_land((x, y)):
                biome = world.biome_at((x, y))
                pixels[x, y] = biome_colors[biome]
            else:
                c = int(world.sea_depth[y][x] * 200 + 50)
                pixels[x, y] = (0, 0, 255 - c, 255)

    counter.printself()
    img.save(filename)


def draw_temperature_levels(world, filename):
    WIDTH = world.width
    HEIGHT = world.height

    img = Image.new('RGBA', (WIDTH, HEIGHT))

    pixels = img.load()
    for y in range(0, HEIGHT):
        for x in range(0, WIDTH):
            if world.is_temperature_polar((x, y)):
                pixels[x, y] = (0, 0, 255, 255)
            elif world.is_temperature_alpine((x, y)):
                pixels[x, y] = (42, 0, 213, 255)
            elif world.is_temperature_boreal((x, y)):
                pixels[x, y] = (85, 0, 170, 255)
            elif world.is_temperature_cool((x, y)):
                pixels[x, y] = (128, 0, 128, 255)
            elif world.is_temperature_warm((x, y)):
                pixels[x, y] = (170, 0, 85, 255)
            elif world.is_temperature_subtropical((x, y)):
                pixels[x, y] = (213, 0, 42, 255)
            elif world.is_temperature_tropical((x, y)):
                pixels[x, y] = (255, 0, 0, 255)

    img.save(filename)


biome_colors = {
    'ocean': (23, 94, 145),
    'ice' : (255, 255, 255),
    'subpolar dry tundra': (128, 128, 128),
    'subpolar moist tundra': (96, 128, 128),
    'subpolar wet tundra': (64, 128, 128),
    'subpolar rain tundra': (32, 128, 192),
    'polar desert' : (192, 192, 192),
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


def draw_biome(temp, filename):
    WIDTH = len(temp[0])
    HEIGHT = len(temp)

    img = Image.new('RGBA', (WIDTH, HEIGHT))
    pixels = img.load()

    for y in range(0, HEIGHT):
        for x in range(0, WIDTH):
            v = temp[y][x]
            pixels[x, y] = biome_colors[v]
    img.save(filename)  
