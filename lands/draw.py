__author__ = 'Federico Tomassetti'

from PIL import Image

try:
    from worldgen.geo import N_PLATES, MAX_ELEV, antialias
except:
    from geo import N_PLATES, MAX_ELEV, antialias

from biome import *


def draw_plates(plates, filename):
    WIDTH = len(plates[0])
    HEIGHT = len(plates)

    img = Image.new('RGBA', (WIDTH, HEIGHT))
    pixels = img.load()
    for y in range(0, HEIGHT):
        for x in range(0, WIDTH):
            n = plates[y][x] * 255 / N_PLATES
            pixels[x, y] = (n, n, n, 255)
    img.save(filename)


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


def draw_simple_elevation(data, filename, shadow, width, height):
    COLOR_STEP = 1.5

    def my_color(c):
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

    img = Image.new('RGBA', (width, height))
    pixels = img.load()

    min_elev = None
    max_elev = None
    for y in xrange(height):
        for x in xrange(width):
            e = data[y * width + x]
            if min_elev == None or e < min_elev:
                min_elev = e
            if max_elev == None or e > max_elev:
                max_elev = e
    elev_delta = max_elev - min_elev

    for y in range(0, height):
        for x in range(0, width):
            e = data[y * width + x]
            # c = 255-int(((e-min_elev)*255)/elev_delta)
            #pixels[x,y] = (c,c,c,255)
            r, g, b = my_color(e)
            pixels[x, y] = (int(r * 255), int(g * 255), int(b * 255), 255)
    img.save(filename)


def find_land_borders(world):
    _borders = [[False for x in xrange(world.width)] for y in xrange(world.height)]
    for y in xrange(world.height):
        for x in xrange(world.width):
            if not world.ocean[y][x] and world.tiles_around((x, y), radius=1, predicate=world.is_ocean):
                _borders[y][x] = True
    return _borders


def find_mountains_mask(world):
    _mask = [[False for x in xrange(world.width)] for y in xrange(world.height)]
    for y in xrange(world.height):
        for x in xrange(world.width):
            if world.is_mountain((x, y)):
                v = len(world.tiles_around((x, y), radius=3, predicate=world.is_mountain))
                if v > 32:
                    _mask[y][x] = v / 4
    return _mask


def mask(world, predicate):
    _mask = [[False for x in xrange(world.width)] for y in xrange(world.height)]
    for y in xrange(world.height):
        for x in xrange(world.width):
            if predicate((x, y)):
                v = len(world.tiles_around((x, y), radius=1, predicate=predicate))
                if v > 5:
                    _mask[y][x] = v
    return _mask


def find_forest_mask(world):
    return mask(world, predicate=world.is_forest)


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


def draw_forest(pixels, x, y, w, h):
    # pixels[x,y] =
    c = (0, 64, 0, 255)
    c2 = (0, 100, 0, 255)
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


def draw_jungle(pixels, x, y, w, h):
    # pixels[x,y] =
    c = (0, 164, 0, 255)
    c2 = (0, 200, 0, 255)
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


def draw_savanna(pixels, x, y, w, h):
    c = (181, 149, 20, 255)
    c2 = (105, 95, 58, 255)
    for dx in xrange(-1, 1):
        pixels[x + dx, y - 2] = c
    for dx in xrange(-2, 2):
        pixels[x + dx, y - 1] = c
    for dx in xrange(-1, 1):
        pixels[x + dx, y - 0] = c
    pixels[x, y + 1] = c2
    pixels[x, y + 2] = c2


def draw_tundra(pixels, x, y, w, h):
    # pixels[x,y] =
    c = (30, 82, 80, 255)
    c2 = (30, 110, 80, 255)
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


def draw_desert(pixels, x, y, w, h):
    c = (245, 245, 140, 255)
    l = (181, 166, 127, 255)  # land_color
    pixels[x - 1, y - 1] = c
    pixels[x - 0, y - 1] = c
    pixels[x + 1, y - 1] = c
    pixels[x - 2, y - 0] = c
    pixels[x + 2, y - 0] = c
    pixels[x - 3, y + 1] = c
    pixels[x + 3, y + 1] = c

    pixels[x - 1, y + 0] = l
    pixels[x - 0, y + 0] = l
    pixels[x + 1, y + 0] = l
    pixels[x - 2, y + 1] = l
    pixels[x - 1, y + 1] = l
    pixels[x + 0, y + 1] = l
    pixels[x + 1, y + 1] = l
    pixels[x + 2, y + 1] = l


def draw_rock_desert(pixels, x, y, w, h):
    c = (71, 74, 65, 255)
    l = (181, 166, 127, 255)  # land_color
    pixels[x - 1, y - 1] = c
    pixels[x - 0, y - 1] = c
    pixels[x + 1, y - 1] = c
    pixels[x - 2, y - 0] = c
    pixels[x + 2, y - 0] = c
    pixels[x - 3, y + 1] = c
    pixels[x + 3, y + 1] = c

    pixels[x - 1, y + 0] = l
    pixels[x - 0, y + 0] = l
    pixels[x + 1, y + 0] = l
    pixels[x - 2, y + 1] = l
    pixels[x - 1, y + 1] = l
    pixels[x + 0, y + 1] = l
    pixels[x + 1, y + 1] = l
    pixels[x + 2, y + 1] = l


def draw_a_mountain(pixels, x, y, w=3, h=3):
    mcl = (0, 0, 0, 255)
    mcll = (128, 128, 128, 255)
    mcr = (75, 75, 75, 255)
    # left edge
    for mody in range(-h, h + 1):
        bottomness = (float(mody + h) / 2.0) / w
        leftborder = int(bottomness * w)
        darkarea = int(bottomness * w) / 2
        lightarea = int(bottomness * w) / 2
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


def draw_glacier(pixels, x, y):
    rg = 255 - (x ** (y / 5) + x * 23 + y * 37 + (x * y) * 13) % 75
    pixels[x, y] = (rg, rg, 255, 255)


def pseudo_random_land_pos(world, i):
    y = (i ** 7 + i * 23) % world.height
    x = (i ** 13 + i * 37) % world.width
    if world.is_land((x, y)):
        return (int(x), int(y))
    else:
        return pseudo_random_land_pos(world, (i % 123456789) * 17 + 11)


def generate_riversmap(world_path, map_path):
    import pickle

    with open(world_path, 'r') as f:
        w = pickle.load(f)

    # Generate images
    draw_riversmap(w, map_path)


def draw_river(world, pixels, pos):
    if world.is_ocean(pos):
        return
    x, y = pos
    pixels[x, y] = (0, 0, 128, 255)
    draw_river(world, pixels, lowest_neighbour(world, pos))


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


def draw_riversmap_on_image(world, pixels):
    sea_color = (0, 0, 128, 255)
    land_color = (255, 255, 255, 255)

    for i in range(1, 45):
        candidates = []
        for j in range(1, 10):
            candidates.append(pseudo_random_land_pos(world, i * j + j))
        max = None
        cc = None
        for c in candidates:
            cx, cy = c
            wl = world.humidity['data'][cy][cx] * world.precipitation['data'][cy][cx] * world.elevation['data'][cy][cx]
            if max == None or wl > max:
                max = wl
                cc = c
        draw_river(world, pixels, cc)


def draw_riversmap(world, filename):
    img = Image.new('RGBA', (world.width, world.height))
    pixels = img.load()

    for y in xrange(world.height):
        for x in xrange(world.width):
            if world.ocean[y][x]:
                pixels[x, y] = sea_color
            else:
                pixels[x, y] = land_color

    draw_riversmap_on_image(world, pixels)

    img.save(filename)


def draw_oldmap(world):
    img = Image.new('RGBA', (world.width, world.height))
    pixels = img.load()

    sea_color = (212, 198, 169, 255)
    land_color = (181, 166, 127, 255)
    borders = find_land_borders(world)
    mountains_mask = find_mountains_mask(world)
    forest_mask = find_forest_mask(world)
    jungle_mask = mask(world, world.is_jungle)
    desert_mask = mask(world, world.is_sand_desert)
    rock_desert_mask = mask(world, world.is_rock_desert)
    tundra_mask = mask(world, world.is_tundra)
    savanna_mask = mask(world, world.is_savanna)

    def unset_mask(pos):
        x, y = pos
        mountains_mask[y][x] = False

    def unset_forest_mask(pos):
        x, y = pos
        forest_mask[y][x] = False

    def unset_jungle_mask(pos):
        x, y = pos
        jungle_mask[y][x] = False

    def unset_tundra_mask(pos):
        x, y = pos
        tundra_mask[y][x] = False

    def unset_savanna_mask(pos):
        x, y = pos
        savanna_mask[y][x] = False

    def unset_desert_mask(pos):
        x, y = pos
        desert_mask[y][x] = False

    def unset_rock_desert_mask(pos):
        x, y = pos
        rock_desert_mask[y][x] = False

    def on_border(pos):
        x, y = pos
        return borders[y][x]

    min_elev = None
    max_elev = None
    for y in xrange(world.height):
        for x in xrange(world.width):
            e = world.elevation['data'][y][x]
            if min_elev == None or e < min_elev:
                min_elev = e
            if max_elev == None or e > max_elev:
                max_elev = e
    elev_delta = max_elev - min_elev

    for y in xrange(world.height):
        for x in xrange(world.width):
            e = world.elevation['data'][y][x]
            c = int(((e - min_elev) * 255) / elev_delta)
            if borders[y][x]:
                pixels[x, y] = (0, 0, 0, 255)
            elif world.ocean[y][x]:
                pixels[x, y] = sea_color
            else:
                pixels[x, y] = land_color

    # Draw glacier
    for y in xrange(world.height):
        for x in xrange(world.width):
            if not borders[y][x] and world.is_iceland((x, y)):
                draw_glacier(pixels, x, y)

    # Draw forest
    for y in xrange(world.height):
        for x in xrange(world.width):
            if forest_mask[y][x]:
                w = 2
                h = 3
                r = 3
                if len(world.tiles_around((x, y), radius=r, predicate=on_border)) <= 2:
                    draw_forest(pixels, x, y, w=w, h=h)
                    world.on_tiles_around((x, y), radius=r, action=unset_forest_mask)

                    # Draw savanna
    for y in xrange(world.height):
        for x in xrange(world.width):
            if savanna_mask[y][x]:
                w = 2
                h = 2
                r = 3
                if len(world.tiles_around((x, y), radius=r, predicate=on_border)) <= 2:
                    draw_savanna(pixels, x, y, w=w, h=h)
                    world.on_tiles_around((x, y), radius=r, action=unset_savanna_mask)

    # Draw jungle
    for y in xrange(world.height):
        for x in xrange(world.width):
            if jungle_mask[y][x]:
                w = 2
                h = 3
                r = 3
                if len(world.tiles_around((x, y), radius=r, predicate=on_border)) <= 2:
                    draw_jungle(pixels, x, y, w=w, h=h)
                    world.on_tiles_around((x, y), radius=r, action=unset_jungle_mask)

                    # Draw tundra
    for y in xrange(world.height):
        for x in xrange(world.width):
            if tundra_mask[y][x]:
                w = 2
                h = 3
                r = 3
                if len(world.tiles_around((x, y), radius=r, predicate=on_border)) <= 2:
                    draw_tundra(pixels, x, y, w=w, h=h)
                    world.on_tiles_around((x, y), radius=r, action=unset_tundra_mask)

                    # Draw sand desert
    for y in xrange(world.height):
        for x in xrange(world.width):
            if desert_mask[y][x]:
                w = 2
                h = 3
                r = 4
                if len(world.tiles_around((x, y), radius=r, predicate=on_border)) <= 2:
                    draw_desert(pixels, x, y, w=w, h=h)
                    world.on_tiles_around((x, y), radius=r, action=unset_desert_mask)

                    # Draw rock desert
    for y in xrange(world.height):
        for x in xrange(world.width):
            if rock_desert_mask[y][x]:
                w = 2
                h = 3
                r = 4
                if len(world.tiles_around((x, y), radius=r, predicate=on_border)) <= 2:
                    draw_rock_desert(pixels, x, y, w=w, h=h)
                    world.on_tiles_around((x, y), radius=r, action=unset_rock_desert_mask)

    draw_riversmap_on_image(world, pixels)

    # Draw mountains
    for y in xrange(world.height):
        for x in xrange(world.width):
            if mountains_mask[y][x]:
                w = mountains_mask[y][x]
                h = 3 + int(world.level_of_mountain((x, y)))
                r = max(w / 3 * 2, h)
                if len(world.tiles_around((x, y), radius=r, predicate=on_border)) <= 2:
                    draw_a_mountain(pixels, x, y, w=w, h=h)
                    world.on_tiles_around((x, y), radius=r, action=unset_mask)

    return img


def draw_bw_heightmap(world, filename):
    img = Image.new('RGBA', (world.width, world.height))
    pixels = img.load()

    min_elev = None
    max_elev = None
    for y in xrange(world.height):
        for x in xrange(world.width):
            e = world.elevation['data'][y][x]
            if min_elev == None or e < min_elev:
                min_elev = e
            if max_elev == None or e > max_elev:
                max_elev = e
    elev_delta = max_elev - min_elev

    for y in xrange(world.height):
        for x in xrange(world.width):
            e = world.elevation['data'][y][x]
            c = int(((e - min_elev) * 255) / elev_delta)
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
            if min_elev == None or e < min_elev:
                min_elev = e
            if max_elev == None or e > max_elev:
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
                if min_elev == None or e < min_elev:
                    min_elev = e
                if max_elev == None or e > max_elev:
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
                if min_elev == None or e < min_elev:
                    min_elev = e
                if max_elev == None or e > max_elev:
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
                if min_elev == None or e < min_elev:
                    min_elev = e
                if max_elev == None or e > max_elev:
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
    WIDTH = world.width
    HEIGHT = world.height

    ocean = world.ocean
    img = Image.new('RGBA', (WIDTH, HEIGHT))
    pixels = img.load()

    # min_elev = None
    # max_elev = None
    # for y in xrange(HEIGHT):
    # for x in xrange(WIDTH):
    #       if not ocean[y][x]:
    #           e = _watermap[y][x]**1.5
    #           if min_elev==None or e<min_elev:
    #               min_elev=e
    #           if max_elev==None or e>max_elev:
    #               max_elev=e              
    # elev_delta = max_elev-min_elev    
    # if elev_delta<1:
    #   elev_delta=1

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


def draw_basic_elevation(elevation, filename):
    WIDTH = len(elevation[0])
    HEIGHT = len(elevation)

    img = Image.new('RGBA', (WIDTH, HEIGHT))
    pixels = img.load()
    for y in range(0, HEIGHT):
        for x in range(0, WIDTH):
            e = int(elevation[y][x] * 255 / MAX_ELEV)
            if e < 0:
                e = 0
            if e > 255:
                e = 255
            pixels[x, y] = (e, e, e, 255)
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
    WIDTH = world.width
    HEIGHT = world.height

    data = world.precipitation['data']
    ocean = world.ocean
    img = Image.new('RGBA', (WIDTH, HEIGHT))
    pixels = img.load()
    for y in range(0, HEIGHT):
        for x in range(0, WIDTH):
            if ocean[y][x]:
                pixels[x, y] = (0, 0, 0, 255)
            else:
                c = int((data[y][x] + 1.0) * 127.5)
                pixels[x, y] = (0, 0, c, 255)
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


class Counter:
    def __init__(self):
        self.c = {}

    def count(self, what):
        if not what in self.c:
            self.c[what] = 0
        self.c[what] += 1

    def printself(self):
        for w in self.c.keys():
            print("%s : %i" % (w, self.c[w]))


biome_colors = {
    'iceland': (208, 241, 245),
    'jungle': (54, 240, 17),
    'tundra': (180, 120, 130),
    'ocean': (23, 94, 145),
    'forest': (10, 89, 15),
    'grassland': (69, 133, 73),
    'steppe': (90, 117, 92),
    'sand desert': (207, 204, 58),
    'rock desert': (94, 93, 25),
    'swamp': (255, 0, 0),
    'glacier': (255, 255, 255),
    'alpine': (100, 70, 5),
    'savanna': (200, 140, 20)
}


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
            if world.is_land((x, y)):
                e = world.elevation['data'][y][x]
                if world.is_temperature_very_low((x, y)):
                    pixels[x, y] = (0, 0, 255, 255)
                elif world.is_temperature_low((x, y)):
                    pixels[x, y] = (80, 120, 255, 255)
                elif world.is_temperature_medium((x, y)):
                    pixels[x, y] = (180, 255, 180, 255)
                elif world.is_temperature_high((x, y)):
                    pixels[x, y] = (255, 0, 0, 255)
            else:
                pixels[x, y] = (0, 0, 0, 255)
    img.save(filename)


biome_colors = {
    'iceland': (208, 241, 245),
    'jungle': (54, 240, 17),
    'tundra': (180, 120, 130),
    'ocean': (23, 94, 145),
    'forest': (10, 89, 15),
    'grassland': (69, 133, 73),
    'steppe': (90, 117, 92),
    'sand desert': (207, 204, 58),
    'rock desert': (94, 93, 25),
    'swamp': (255, 0, 0),
    'glacier': (255, 255, 255),
    'alpine': (100, 70, 5),
    'savanna': (200, 140, 20)
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
