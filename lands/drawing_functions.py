__author__ = 'Federico Tomassetti'

# This file should contain only functions that operates on pixels, not on images,
# so no references to PIL are necessary and the module can be used also through
# Jython

def find_land_borders(world, factor):
    _ocean   = [[False for x in xrange(factor*world.width)] for y in xrange(factor*world.height)]
    _borders = [[False for x in xrange(factor*world.width)] for y in xrange(factor*world.height)]
    for y in xrange(world.height*factor):
        for x in xrange(world.width*factor):
            if world.ocean[y/factor][x/factor]:
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
            if world.is_mountain((x/factor, y/factor)):
                v = len(world.tiles_around((x/factor, y/factor), radius=3, predicate=world.is_mountain))
                if v > 32:
                    _mask[y][x] = v / 4
    return _mask


def mask(world, predicate, factor):
    _mask = [[False for x in xrange(factor*world.width)] for y in xrange(factor*world.height)]
    for y in xrange(factor*world.height):
        for x in xrange(factor*world.width):
            if predicate((x/factor, y/factor)):
                v = len(world.tiles_around((x/factor, y/factor), radius=1, predicate=predicate))
                if v > 5:
                    _mask[y][x] = v
    return _mask


def find_forest_mask(world, factor):
    return mask(world, predicate=world.is_forest, factor=factor)


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


def draw_oldmap_on_pixels(world, pixels, factor=1):
    sea_color = (212, 198, 169, 255)
    land_color = (181, 166, 127, 255)
    borders = find_land_borders(world, factor)
    mountains_mask = find_mountains_mask(world, factor)
    forest_mask = find_forest_mask(world, factor)
    jungle_mask = mask(world, world.is_jungle, factor)
    desert_mask = mask(world, world.is_sand_desert, factor)
    rock_desert_mask = mask(world, world.is_rock_desert, factor)
    tundra_mask = mask(world, world.is_tundra, factor)
    savanna_mask = mask(world, world.is_savanna, factor)

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

    for y in xrange(factor*world.height):
        for x in xrange(factor*world.width):
            e = world.elevation['data'][y/factor][x/factor]
            c = int(((e - min_elev) * 255) / elev_delta)
            if borders[y][x]:
                pixels[x, y] = (0, 0, 0, 255)
            elif world.ocean[y/factor][x/factor]:
                pixels[x, y] = sea_color
            else:
                pixels[x, y] = land_color

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
            r = (tot_r/n)
            g = (tot_g/n)
            b = (tot_b/n)
            pixels[x, y] = (r,g,b,255)

        for i in range(0, steps):
            _antialias_step()

    antialias(1)

    # Draw glacier
    for y in xrange(factor*world.height):
        for x in xrange(factor*world.width):
            if not borders[y][x] and world.is_iceland((x/factor, y/factor)):
                draw_glacier(pixels, x, y)

    # Draw forest
    for y in xrange(factor*world.height):
        for x in xrange(factor*world.width):
            if forest_mask[y][x]:
                w = 2
                h = 3
                r = 3
                if len(world.tiles_around_factor(factor, (x, y), radius=r, predicate=on_border)) <= 2:
                    draw_forest(pixels, x, y, w=w, h=h)
                    world.on_tiles_around_factor(factor, (x, y), radius=r, action=unset_forest_mask)

    # Draw savanna
    for y in xrange(factor*world.height):
        for x in xrange(factor*world.width):
            if savanna_mask[y][x]:
                w = 2
                h = 2
                r = 3
                if len(world.tiles_around_factor(factor, (x, y), radius=r, predicate=on_border)) <= 2:
                    draw_savanna(pixels, x, y, w=w, h=h)
                    world.on_tiles_around_factor(factor, (x, y), radius=r, action=unset_savanna_mask)

    # Draw jungle
    for y in xrange(factor*world.height):
        for x in xrange(factor*world.width):
            if jungle_mask[y][x]:
                w = 2
                h = 3
                r = 3
                if len(world.tiles_around_factor(factor, (x, y), radius=r, predicate=on_border)) <= 2:
                    draw_jungle(pixels, x, y, w=w, h=h)
                    world.on_tiles_around_factor(factor, (x, y), radius=r, action=unset_jungle_mask)

                    # Draw tundra
    for y in xrange(factor*world.height):
        for x in xrange(factor*world.width):
            if tundra_mask[y][x]:
                w = 2
                h = 3
                r = 3
                if len(world.tiles_around_factor(factor, (x, y), radius=r, predicate=on_border)) <= 2:
                    draw_tundra(pixels, x, y, w=w, h=h)
                    world.on_tiles_around_factor(factor, (x, y), radius=r, action=unset_tundra_mask)

    # Draw sand desert
    for y in xrange(factor*world.height):
        for x in xrange(factor*world.width):
            if desert_mask[y][x]:
                w = 2
                h = 3
                r = 4
                if len(world.tiles_around_factor(factor, (x, y), radius=r, predicate=on_border)) <= 2:
                    draw_desert(pixels, x, y, w=w, h=h)
                    world.on_tiles_around_factor(factor, (x, y), radius=r, action=unset_desert_mask)

    # Draw rock desert
    for y in xrange(factor*world.height):
        for x in xrange(factor*world.width):
            if rock_desert_mask[y][x]:
                w = 2
                h = 3
                r = 4
                if len(world.tiles_around_factor(factor, (x, y), radius=r, predicate=on_border)) <= 2:
                    draw_rock_desert(pixels, x, y, w=w, h=h)
                    world.on_tiles_around_factor(factor, (x, y), radius=r, action=unset_rock_desert_mask)

    draw_riversmap_on_image(world, pixels, factor)

    # Draw mountains
    for y in xrange(factor*world.height):
        for x in xrange(factor*world.width):
            if mountains_mask[y][x]:
                w = mountains_mask[y][x]
                h = 3 + int(world.level_of_mountain((x/factor, y/factor)))
                r = max(w / 3 * 2, h)
                if len(world.tiles_around_factor(factor, (x, y), radius=r, predicate=on_border)) <= 2:
                    draw_a_mountain(pixels, x, y, w=w, h=h)
                    world.on_tiles_around_factor(factor, (x, y), radius=r, action=unset_mask)

    return pixels


def draw_riversmap_on_image(world, pixels, factor):
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
