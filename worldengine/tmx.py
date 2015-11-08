from biome import Biome, biome_name_to_index

import numpy

TOCEAN = 366
TLAND  = 244
TLAND_E_S_SE = 260
TLAND_W_SW_S = 261
TLAND_N_NE_E = 281
TLAND_NW_N_W = 282
TLAND_BUT_SE = 301
TLAND_BUT_SW = 303
TLAND_BUT_NE = 343
TLAND_BUT_NW = 345
TLAND_COAST_N = 302
TLAND_COAST_W = 322
TLAND_COAST_E = 324
TLAND_COAST_S = 344
T_ISLAND = 277
TRIVER = 363

TMOUNTAIN = 484
TFOREST = 485


def get_land_around(world, x, y):
    s = y + 1
    if s == world.height:
        s = 0
    n = y - 1
    if n == -1:
        n = world.height - 1
    e = x + 1
    if e == world.width:
        e = 0
    w = x - 1
    if w == -1:
        w = world.width - 1
    return [world.is_land((w,n)),world.is_land((x,n)),world.is_land((e,n)),world.is_land((w,y)),world.is_land((e,y)),world.is_land((w,s)),world.is_land((x,s)),world.is_land((e,s))]


def get_river_around(world, x, y):
    s = y + 1
    if s == world.height:
        s = 0
    n = y - 1
    if n == -1:
        n = world.height - 1
    e = x + 1
    if e == world.width:
        e = 0
    w = x - 1
    if w == -1:
        w = world.width - 1
    return [world.river_map[w, n] > 0 or world.is_ocean((w, n)),
            world.river_map[x, n] > 0 or world.is_ocean((x, n)),
            world.river_map[e, n] > 0 or world.is_ocean((e, n)),
            world.river_map[w, y] > 0 or world.is_ocean((w, y)),
            world.river_map[e, y] > 0 or world.is_ocean((e, y)),
            world.river_map[w, s] > 0 or world.is_ocean((w, s)),
            world.river_map[x, s] > 0 or world.is_ocean((x, s)),
            world.river_map[e, s] > 0 or world.is_ocean((e, s))]


def _transform_for_tmx(world):

    # each river point with 2 or more tiles of ocean in N, S, E, W is transformed
    # in an ocean tile
    for y in range(world.height):
        for x in range(world.width):
            if world.river_map[x, y] > 0:
                ocean_around = [(not v) for v in get_land_around(world,x,y)]
                oceans = 0
                if ocean_around[1]:
                    oceans = oceans + 1
                if ocean_around[3]:
                    oceans = oceans + 1
                if ocean_around[4]:
                    oceans = oceans + 1
                if ocean_around[6]:
                    oceans = oceans + 1
                if oceans >= 2:
                    world.ocean[y, x] = True

    # remove small pieces of land between rivers and ocean
    for y in range(world.height):
        for x in range(world.width):
            if world.is_land((x, y)):
                river_around = get_river_around(world,x,y)
                ocean_around = [(not v) for v in get_land_around(world,x,y)]
                if ocean_around[1] and ocean_around[6] and ocean_around[3] and river_around[4]:
                    world.ocean[y, x] = True
                elif river_around[1] and ocean_around[3] and ocean_around[6]:
                    world.ocean[y, x] = True
                elif river_around[6] and ocean_around[1] and ocean_around[2]:
                    world.ocean[y, x] = True


WG_LAND  = 0
WG_OCEAN = 1
WG_RIVER = 2


def water_cell_grid(world, pos):
    """
    Given a position calculate a grid 3x3 to determine where there should be water and
    where it should not be water
    :param world:
    :param pos:
    :return:
    """
    x, y = pos

    if world.is_ocean(pos):
        return [[WG_OCEAN, WG_OCEAN, WG_OCEAN], [WG_OCEAN, WG_OCEAN, WG_OCEAN], [WG_OCEAN, WG_OCEAN, WG_OCEAN]]
    elif world.is_river(pos):
        ocean_around = [(not v) for v in get_land_around(world, x, y)]
        river_around = get_river_around(world, x, y)
        top = [WG_LAND, WG_LAND, WG_LAND]
        if river_around[1] or ocean_around[1]:
            top[1] = WG_RIVER
        middle = [WG_LAND, WG_RIVER, WG_LAND]
        if river_around[3] or ocean_around[3]:
            middle[0] = WG_RIVER
        if river_around[4] or ocean_around[4]:
            middle[2] = WG_RIVER
        bottom = [WG_LAND, WG_LAND, WG_LAND]
        if river_around[6] or ocean_around[6]:
            bottom[1] = WG_RIVER
        return [top, middle, bottom]
    else:
        return [[WG_LAND, WG_LAND, WG_LAND], [WG_LAND, WG_LAND, WG_LAND], [WG_LAND, WG_LAND, WG_LAND]]


def grid_coords(world, pos, dy, dx, mov_x, mov_y):
    x, y = pos
    ndx = dx + mov_x
    ndy = dy + mov_y
    if ndx == 3:
        ndx = 0
        x = x + 1
    if ndx == -1:
        ndx = 2
        x = x - 1
    if ndy == 3:
        ndy = 0
        y = y + 1
    if ndy == -1:
        ndy = 2
        y = y - 1
    if x == -1:
        x = world.width - 1
    if x == world.width:
        x = 0
    if y == -1:
        y = world.height - 1
    if y == world.height:
        y = 0
    return (x, y), ndx, ndy


def is_water_tile(water_grid, gx, gy):
    return water_grid[gx, gy] != WG_LAND


def is_ocean_tile(water_grid, gx, gy):
    return water_grid[gx, gy] == WG_OCEAN


def is_river_tile(water_grid, gx, gy):
    return water_grid[gx, gy] == WG_RIVER


def tiles_around(water_grid, gx, gy):
    gxw = gx - 1
    if gxw == -1:
        gxw = water_grid.shape[1] - 1
    gxe = gx + 1
    if gxe == water_grid.shape[1]:
        gxe = 0
    gyn = gy - 1
    if gyn == -1:
        gyn = water_grid.shape[0] - 1
    gys = gy + 1
    if gys == water_grid.shape[0] - 1:
        gys = 0
    return [(gxw, gyn),
            (gx,  gyn),
            (gxe, gyn),
            (gxw, gy),
            (gxe, gy),
            (gxw, gys),
            (gx,  gys),
            (gxe, gys)]


def water_tiles_around(water_grid, gx, gy):
    gxw = gx - 1
    if gxw == -1:
        gxw = water_grid.shape[1] - 1
    gxe = gx + 1
    if gxe == water_grid.shape[1]:
        gxe = 0
    gyn = gy - 1
    if gyn == -1:
        gyn = water_grid.shape[0] - 1
    gys = gy + 1
    if gys == water_grid.shape[0] - 1:
        gys = 0
    return [is_water_tile(water_grid, gxw, gyn),
            is_water_tile(water_grid, gx,  gyn),
            is_water_tile(water_grid, gxe, gyn),
            is_water_tile(water_grid, gxw, gy),
            is_water_tile(water_grid, gxe, gy),
            is_water_tile(water_grid, gxw, gys),
            is_water_tile(water_grid, gx,  gys),
            is_water_tile(water_grid, gxe, gys),]


def river_tiles_around(water_grid, gx, gy):
    gxw = gx - 1
    if gxw == -1:
        gxw = water_grid.shape[1] - 1
    gxe = gx + 1
    if gxe == water_grid.shape[1]:
        gxe = 0
    gyn = gy - 1
    if gyn == -1:
        gyn = water_grid.shape[0] - 1
    gys = gy + 1
    if gys == water_grid.shape[0] - 1:
        gys = 0
    return [is_river_tile(water_grid, gxw, gyn),
            is_river_tile(water_grid, gx,  gyn),
            is_river_tile(water_grid, gxe, gyn),
            is_river_tile(water_grid, gxw, gy),
            is_river_tile(water_grid, gxe, gy),
            is_river_tile(water_grid, gxw, gys),
            is_river_tile(water_grid, gx,  gys),
            is_river_tile(water_grid, gxe, gys),]


def ocean_tiles_around(water_grid, gx, gy):
    gxw = gx - 1
    if gxw == -1:
        gxw = water_grid.shape[1] - 1
    gxe = gx + 1
    if gxe == water_grid.shape[1]:
        gxe = 0
    gyn = gy - 1
    if gyn == -1:
        gyn = water_grid.shape[0] - 1
    gys = gy + 1
    if gys == water_grid.shape[0] - 1:
        gys = 0
    return [is_ocean_tile(water_grid, gxw, gyn),
            is_ocean_tile(water_grid, gx,  gyn),
            is_ocean_tile(water_grid, gxe, gyn),
            is_ocean_tile(water_grid, gxw, gy),
            is_ocean_tile(water_grid, gxe, gy),
            is_ocean_tile(water_grid, gxw, gys),
            is_ocean_tile(water_grid, gx,  gys),
            is_ocean_tile(water_grid, gxe, gys),]


def terrain_grid_value(water_grid, gx, gy):
    wg_tile = water_grid[gx, gy]
    if wg_tile == WG_LAND:
        water_around = water_tiles_around(water_grid, gx, gy)

        #
        # No water
        #

        if water_around == [False, False, False, False, False, False, False, False]:
            return TLAND

        #
        # Water on one side
        #

        elif not water_around[1] and not water_around[3] and not water_around[4] and water_around[6]:
            return TLAND_COAST_N
        elif water_around[1] and not water_around[3] and not water_around[4] and not water_around[6]:
            return TLAND_COAST_S
        elif not water_around[1] and water_around[3] and not water_around[4] and not water_around[6]:
            return TLAND_COAST_E
        elif not water_around[1] and not water_around[3] and water_around[4] and not water_around[6]:
            return TLAND_COAST_W

        #
        # Water in diagonal
        #

        elif water_around == [True, False, False, False, False, False, False, False]:
            return TLAND_BUT_NW
        elif water_around == [False, False, True, False, False, False, False, False]:
            return TLAND_BUT_NE
        elif water_around == [False, False, False, False, False, True, False, False]:
            return TLAND_BUT_SW
        elif water_around == [False, False, False, False, False, False, False, True]:
            return TLAND_BUT_SE

        #
        # Water on two sides
        #

        elif water_around[1] and water_around[3] and not water_around[4] and not water_around[6]:
            return TLAND_E_S_SE
        elif water_around[1] and not water_around[3] and water_around[4] and not water_around[6]:
            return TLAND_W_SW_S
        elif not water_around[1] and water_around[3] and not water_around[4] and water_around[6]:
            return TLAND_N_NE_E
        elif not water_around[1] and not water_around[3] and water_around[4] and water_around[6]:
            return TLAND_NW_N_W

        elif water_around == [True, True, True, True, True, True, True, True]:
            return T_ISLAND

        else:
            raise Exception(str(water_around))
    elif wg_tile == WG_RIVER:
        return TRIVER
    elif wg_tile == WG_OCEAN:
        return TOCEAN
    else:
        raise Exception("Unknown water grid cell. Found %i" % wg_tile)


def clean_water_grid(water_grid):

    def clean_single_cell(gx, gy):
        wg_tile = water_grid[gx, gy]
        if wg_tile == WG_LAND:
            water_around = water_tiles_around(water_grid, gx, gy)

            #
            # No water
            #

            if water_around == [False, False, False, False, False, False, False, False]:
                pass

            #
            # Water on one side
            #

            elif not water_around[1] and not water_around[3] and not water_around[4] and water_around[6]:
                pass
            elif water_around[1] and not water_around[3] and not water_around[4] and not water_around[6]:
                pass
            elif not water_around[1] and water_around[3] and not water_around[4] and not water_around[6]:
                pass
            elif not water_around[1] and not water_around[3] and water_around[4] and not water_around[6]:
                pass

            #
            # Water in diagonal
            #

            elif water_around == [True, False, False, False, False, False, False, False]:
                pass
            elif water_around == [False, False, True, False, False, False, False, False]:
                pass
            elif water_around == [False, False, False, False, False, True, False, False]:
                pass
            elif water_around == [False, False, False, False, False, False, False, True]:
                pass

            #
            # Water on two sides
            #

            elif water_around[1] and water_around[3] and not water_around[4] and not water_around[6]:
                pass
            elif water_around[1] and not water_around[3] and water_around[4] and not water_around[6]:
                pass
            elif not water_around[1] and water_around[3] and not water_around[4] and water_around[6]:
                pass
            elif not water_around[1] and not water_around[3] and water_around[4] and water_around[6]:
                pass

            elif water_around == [True, True, True, True, True, True, True, True]:
                pass

            else:
                water_grid[gx, gy] = WG_RIVER
                for around in tiles_around(water_grid, gx, gy):
                    around_x, around_y = around
                    clean_single_cell(around_x, around_y)

    for gx in range(water_grid.shape[0]):
        for gy in range(water_grid.shape[1]):
            clean_single_cell(gx, gy)


def generate_water_grid(world):
    water_grid = numpy.zeros(shape=(world.width * 3, world.height * 3))
    for y in range(world.height):
        for x in range(world.width):
            pos = (x, y)
            cell = water_cell_grid(world, pos)
            for dy in range(3):
                for dx in range(3):
                    water_grid[x * 3 + dx, y * 3 + dy] = cell[dy][dx]
    return water_grid


def export_to_tmx_orthogonal(world, tmx_filename):
    # We perform some preliminary transformation to make the world
    # nicer for a tiled map
    #_transform_for_tmx(world)

    tmx_file = open(tmx_filename, "w")
    tmx_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    tmx_file.write('<map version="1.0" orientation="orthogonal" renderorder="right-down" width="%i" height="%i" tilewidth="32" tileheight="32" nextobjectid="1">\n' % (world.width*3, world.height*3))
    tmx_file.write('<tileset firstgid="1" name="T2" tilewidth="32" tileheight="32" tilecount="483">\n')
    tmx_file.write('<image source="terrain_2.png" width="672" height="736"/>\n')
    tmx_file.write('</tileset>\n')
    tmx_file.write('<tileset firstgid="484" name="Mountain" tilewidth="96" tileheight="96" tilecount="1">\n')
    tmx_file.write('<tile id="0">\n')
    tmx_file.write('<image width="96" height="96" source="m.png"/>\n')
    tmx_file.write('</tile>\n')
    tmx_file.write('<tile id="1">\n')
    tmx_file.write('<image width="96" height="96" source="tree.png"/>\n')
    tmx_file.write('</tile>\n')
    tmx_file.write('</tileset>\n')

    tmx_file.write('  <layer name="biome" width="%i" height="%i">\n' % (world.width*3, world.height*3))
    tmx_file.write('    <data encoding="csv">\n')

    water_grid = generate_water_grid(world)
    clean_water_grid(water_grid)

    for gy in range(world.height * 3):
        for gx in range(world.width * 3):
            grid_value = terrain_grid_value(water_grid, gx, gy)
            tmx_file.write(str(grid_value))
            if gy != (world.height * 3 - 1) or (gx != world.width * 3 - 1):
                tmx_file.write(',')
        tmx_file.write('\n')
    tmx_file.write('    </data>\n')
    tmx_file.write('  </layer>\n')

    tmx_file.write('  <layer name="mountains" width="%i" height="%i">\n' % (world.width*3, world.height*3))
    tmx_file.write('    <data encoding="csv">\n')

    for y in range(world.height):
        for dy in range(3):
            for x in range(world.width):
                pos = (x, y)
                indexes = [0, 0, 0]
                land_around = get_land_around(world,x,y)
                if land_around==[True,True,True,True,True,True,True,True] and world.river_map[x, y] == 0.0:
                    if world.is_mountain(pos):
                        if dy == 1:
                            indexes = [TMOUNTAIN, 0, 0]
                    elif world.is_temperate_forest((x,y)):
                        if dy == 0:
                            indexes = [0, TFOREST, 0]
                        elif dy == 1:
                            indexes = [TFOREST, 0, TFOREST]
                        else:
                            indexes = [0, TFOREST, 0]
                tmx_file.write(str(indexes[0]))
                tmx_file.write(',')
                tmx_file.write(str(indexes[1]))
                tmx_file.write(',')
                tmx_file.write(str(indexes[2]))
                if y != (world.height - 1) or (x != world.width - 1) or dy != 2:
                    tmx_file.write(',')
            tmx_file.write('\n')

    tmx_file.write('    </data>\n')
    tmx_file.write('  </layer>\n')

    tmx_file.write('</map>\n')
    tmx_file.close()


def elev_level(world, pos):
    if world.is_hill(pos):
        return 1
    elif world.is_low_mountain(pos):
        return 2
    elif world.is_high_mountain(pos):
        return 4
    elif world.is_mountain(pos):
        return 3
    else:
        return 0


def get_slope_around(world, x, y):
    my_level = elev_level(world, (x,y))
    s = y + 1
    if s == world.height:
        s = 0
    n = y - 1
    if n == -1:
        n = world.height - 1
    e = x + 1
    if e == world.width:
        e = 0
    w = x - 1
    if w == -1:
        w = world.width - 1
    return [elev_level(world,(w,n))-my_level,elev_level(world,(x,n))-my_level,elev_level(world,(e,n))-my_level,
            elev_level(world,(w,y))-my_level,elev_level(world,(e,y))-my_level,
            elev_level(world,(w,s))-my_level,elev_level(world,(x,s))-my_level,elev_level(world,(e,s))-my_level]


ISO_OCEAN = 86
ISO_RIVER = 85
ISO_LAND = 3
ISO_SNOW = 161
ISO_DIRT = 162
ISO_SLOPE_CORNER_BOTTOM_RIGHT = 31
ISO_SLOPE_CORNER_BOTTOM_LEFT = 34
ISO_SLOPE_CORNER_TOP_LEFT = 39
ISO_SLOPE_CORNER_TOP_RIGHT = 36
ISO_SLOPE_LEFT = 33
ISO_SLOPE_RIGHT = 37
ISO_SLOPE_TOP = 32
ISO_SLOPE_BOTTOM = 38
ISO_TALL = 35
ISO_NONE = 0
ISO_GRASS = 115
ISO_SLOPE_CORNER_TOP_LEFT_INTERNAL = 41
ISO_SLOPE_CORNER_BOTTOM_RIGHT_INTERNAL = 43
ISO_SLOPE_CORNER_TOP_RIGHT_INTERNAL = 42
ISO_SLOPE_CORNER_BOTTOM_LEFT_INTERNAL = 44

# 81,82,83

ISO_TLAND_E_S_SE = 100
ISO_TLAND_W_SW_S = 99
ISO_TLAND_N_NE_E = 98
ISO_TLAND_NW_N_W = 97
ISO_TLAND_BUT_SE = 90
ISO_TLAND_BUT_SW = 87
ISO_TLAND_BUT_NE = 84
ISO_TLAND_BUT_NW = 91
ISO_TLAND_COAST_N = 89
ISO_TLAND_COAST_W = 88
ISO_TLAND_COAST_E = 83
ISO_TLAND_COAST_S = 82
ISO_T_ISLAND = 103

ISO_RIVER_VERT_PIPE = 93
ISO_RIVER_HORI_PIPE = 92
ISO_RIVER_TL = 91
ISO_RIVER_TR = 94
ISO_RIVER_BL = 95
ISO_RIVER_BR = 96


def draw_water(world, tmx_file, water_grid, this_lvl):
    def draw_cell(gx, gy):
        x = gx / 3
        y = gy / 3
        dx = gx - x * 3
        dy = gy - y * 3
        lvl = elev_level(world, (x, y))
        if lvl != this_lvl:
            return ISO_NONE
        slope_around = get_slope_around(world, x, y)
        wg_tile = water_grid[gx, gy]
        if wg_tile == WG_LAND:
            if dy == 0 and slope_around[1] != 0:
                return ISO_NONE
            if dy == 2 and slope_around[6] != 0:
                return ISO_NONE
            if dx == 0 and slope_around[3] != 0:
                return ISO_NONE
            if dx == 2 and slope_around[4] != 0:
                return ISO_NONE
            if dx == 0 and dy == 0 and slope_around[0] != 0:
                return ISO_NONE
            if dx == 2 and dy == 0 and slope_around[2] != 0:
                return ISO_NONE
            if dx == 0 and dy == 2 and slope_around[5] != 0:
                return ISO_NONE
            if dx == 2 and dy == 2 and slope_around[7] != 0:
                return ISO_NONE

            else:
                water_around = ocean_tiles_around(water_grid, gx, gy)

                #
                # No water
                #

                if water_around == [False, False, False, False, False, False, False, False]:
                    return ISO_NONE

                #
                # Water on one side
                #

                elif not water_around[1] and not water_around[3] and not water_around[4] and water_around[6]:
                    return ISO_TLAND_COAST_N
                elif water_around[1] and not water_around[3] and not water_around[4] and not water_around[6]:
                    return ISO_TLAND_COAST_S
                elif not water_around[1] and water_around[3] and not water_around[4] and not water_around[6]:
                    return ISO_TLAND_COAST_E
                elif not water_around[1] and not water_around[3] and water_around[4] and not water_around[6]:
                    return ISO_TLAND_COAST_W

                #
                # Water in diagonal
                #

                elif water_around == [True, False, False, False, False, False, False, False]:
                    return ISO_TLAND_BUT_NW
                elif water_around == [False, False, True, False, False, False, False, False]:
                    return ISO_TLAND_BUT_NE
                elif water_around == [False, False, False, False, False, True, False, False]:
                    return ISO_TLAND_BUT_SW
                elif water_around == [False, False, False, False, False, False, False, True]:
                    return ISO_TLAND_BUT_SE

                #
                # Water on two sides
                #

                elif water_around[1] and water_around[3] and not water_around[4] and not water_around[6]:
                    return ISO_TLAND_E_S_SE
                elif water_around[1] and not water_around[3] and water_around[4] and not water_around[6]:
                    return ISO_TLAND_W_SW_S
                elif not water_around[1] and water_around[3] and not water_around[4] and water_around[6]:
                    return ISO_TLAND_N_NE_E
                elif not water_around[1] and not water_around[3] and water_around[4] and water_around[6]:
                    return ISO_TLAND_NW_N_W

                elif water_around == [True, True, True, True, True, True, True, True]:
                    return ISO_T_ISLAND

                else:
                    raise Exception(str(water_around))
        elif wg_tile == WG_RIVER:
            river_around = river_tiles_around(water_grid, gx, gy)
            if river_around[1] == True and river_around[3] == False and river_around[4] == False and river_around[6] == True:
                return ISO_RIVER_VERT_PIPE
            elif river_around[1] == False and river_around[3] == True and river_around[4] == True and river_around[6] == False:
                return ISO_RIVER_HORI_PIPE
            elif river_around[1] == True and river_around[3] == True and river_around[4] == False and river_around[6] == False:
                return ISO_RIVER_TL
            elif river_around[1] == True and river_around[3] == False and river_around[4] == True and river_around[6] == False:
                return ISO_RIVER_TR
            elif river_around[1] == False and river_around[3] == True and river_around[4] == False and river_around[6] == True:
                return ISO_RIVER_BL
            elif river_around[1] == False and river_around[3] == False and river_around[4] == True and river_around[6] == True:
                return ISO_RIVER_BR
            else:
                return ISO_RIVER
        elif wg_tile == WG_OCEAN:
            return ISO_NONE
        else:
            raise Exception("Unknown water grid cell")

    tmx_file.write('    <data encoding="csv">\n')
    for gy in range(world.height * 3):
        for gx in range(world.width * 3):
            tmx_file.write(str(draw_cell(gx, gy)))
            if gy != (world.height * 3 - 1) or (gx != world.width * 3 - 1):
                tmx_file.write(',')
        tmx_file.write('\n')
    tmx_file.write('    </data>\n')


def draw_level(world, tmx_file, water_grid, this_lvl):
    tmx_file.write('    <data encoding="csv">\n')

    for gy in range(world.height * 3):
        for gx in range(world.width * 3):

            x = int(gx / 3)
            y = int(gy / 3)
            dx = gx - (x*3)
            dy = gy - (y*3)
            lvl = elev_level(world, (x, y))
            if lvl < this_lvl:
                grid_value = ISO_NONE
            elif lvl > this_lvl:
                grid_value = ISO_TALL
            elif world.is_ocean((x, y)):
                grid_value = ISO_OCEAN
            else:
                grid_value = ISO_LAND
                if world.is_cool_desert((x, y)) or world.is_iceland((x, y)) or world.is_cold_parklands((x,y)):
                    grid_value = ISO_SNOW
                elif world.is_hot_desert((x, y)):
                    grid_value = ISO_DIRT
                slope_around = get_slope_around(world, x, y)

                #
                # Sides
                #

                if dy==0 and slope_around[1]>=1:
                    grid_value = ISO_SLOPE_TOP
                if dy==2 and slope_around[6]>=1:
                    grid_value = ISO_SLOPE_BOTTOM
                if dx==0 and slope_around[3]>=1:
                    grid_value = ISO_SLOPE_LEFT
                if dx==2 and slope_around[4]>=1:
                    grid_value = ISO_SLOPE_RIGHT

                #
                # Internal corners
                #

                if dx == 0 and dy == 0 and slope_around[1] >= 1 and slope_around[3] >= 1:
                    grid_value = ISO_SLOPE_CORNER_BOTTOM_RIGHT_INTERNAL
                elif dx == 2 and dy == 0 and slope_around[1] >= 1 and slope_around[4] >= 1:
                    grid_value = ISO_SLOPE_CORNER_BOTTOM_LEFT_INTERNAL
                elif dx == 0 and dy == 2 and slope_around[6] >= 1 and slope_around[3] >= 1:
                    grid_value = ISO_SLOPE_CORNER_TOP_RIGHT_INTERNAL
                elif dx == 2 and dy == 2 and slope_around[6] >= 1 and slope_around[4] >= 1:
                    grid_value = ISO_SLOPE_CORNER_TOP_LEFT_INTERNAL

                #
                # Corners
                #

                if dx == 0 and dy == 0 and slope_around[0] >= 1 and slope_around[1] < 1 and slope_around[3] < 1:
                    grid_value = ISO_SLOPE_CORNER_BOTTOM_RIGHT
                elif dx == 2 and dy == 0 and slope_around[2] >= 1 and slope_around[1] < 1 and slope_around[4] < 1:
                    grid_value = ISO_SLOPE_CORNER_BOTTOM_LEFT
                elif dx == 0 and dy == 2 and slope_around[5] >= 1 and slope_around[6] < 1 and slope_around[3] < 1:
                    grid_value = ISO_SLOPE_CORNER_TOP_RIGHT
                elif dx == 2 and dy == 2 and slope_around[7] >= 1 and slope_around[6] < 1 and slope_around[4] < 1:
                    grid_value = ISO_SLOPE_CORNER_TOP_LEFT


            tmx_file.write(str(grid_value))
            if gy != (world.height * 3 - 1) or (gx != world.width * 3 - 1):
                tmx_file.write(',')
        tmx_file.write('\n')
    tmx_file.write('    </data>\n')


# 134, 124
# 153,143
def draw_forest_level(world, tmx_file, this_lvl):

    forest_grid = numpy.zeros(shape=(world.width * 3, world.height * 3), dtype=numpy.uint16)
    for y in range(world.height):
        for x in range(world.width):
            lvl = elev_level(world, (x, y))
            if lvl == this_lvl:
                if world.is_temperate_forest((x, y)):
                    ta = tiles_around(forest_grid, x * 3, y * 3)
                    forest_grid[ta[0][0], ta[0][1]] = 143
                    forest_grid[ta[7][0], ta[7][1]] = 153
                elif world.is_boreal_forest((x, y)):
                    ta = tiles_around(forest_grid, x * 3, y * 3)
                    forest_grid[ta[0][0], ta[0][1]] = 124
                    forest_grid[ta[7][0], ta[7][1]] = 134
                elif world.is_chaparral((x, y)):
                    forest_grid[x * 3 + 1, y * 3 + 1] = 122

    tmx_file.write('    <data encoding="csv">\n')

    for gy in range(world.height * 3):
        for gx in range(world.width * 3):
            grid_value = forest_grid[gx, gy]
            tmx_file.write(str(grid_value))
            if gy != (world.height * 3 - 1) or (gx != world.width * 3 - 1):
                tmx_file.write(',')
        tmx_file.write('\n')
    tmx_file.write('    </data>\n')


# isometric
def export_to_tmx(world, tmx_filename):
    # We perform some preliminary transformation to make the world
    # nicer for a tiled map
    #_transform_for_tmx(world)

    water_grid = generate_water_grid(world)
    clean_water_grid(water_grid)

    tmx_file = open(tmx_filename, "w")
    tmx_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    tmx_file.write('<map version="1.0" orientation="isometric" renderorder="right-down" width="%i" height="%i" tilewidth="64" tileheight="32" nextobjectid="1">\n' % (world.width*3, world.height*3))
    tmx_file.write('<tileset firstgid="1" name="iso-64x64-outside" tilewidth="64" tileheight="64" tilecount="160">\n')
    tmx_file.write('<image source="iso-64x64-outside.png" width="640" height="1024"/>\n')
    tmx_file.write('</tileset>\n')
    tmx_file.write('<tileset firstgid="161" name="Decorations" tilewidth="64" tileheight="32" tilecount="2">\n')
    tmx_file.write('<tile id="0">\n')
    tmx_file.write('<image width="64" height="32" source="snow.png"/>\n')
    tmx_file.write('</tile>\n')
    tmx_file.write('<tile id="1">\n')
    tmx_file.write('<image width="64" height="32" source="dirt.png"/>\n')
    tmx_file.write('</tile>\n')
    tmx_file.write('</tileset>\n')

    tmx_file.write('  <layer name="ground" width="%i" height="%i">\n' % (world.width*3, world.height*3))
    draw_level(world, tmx_file, water_grid, 0)
    tmx_file.write('  </layer>\n')

    tmx_file.write('  <layer name="ground_water" width="%i" height="%i">\n' % (world.width*3, world.height*3))
    draw_water(world, tmx_file, water_grid, 0)
    tmx_file.write('  </layer>\n')

    tmx_file.write('  <layer name="hill" width="%i" height="%i" offsetx="0" offsety="-32">\n' % (world.width*3, world.height*3))
    draw_level(world, tmx_file, water_grid, 1)
    tmx_file.write('  </layer>\n')

    # tmx_file.write('  <layer name="hill_water" width="%i" height="%i" offsetx="0" offsety="-32">\n' % (world.width*3, world.height*3))
    # draw_water(world, tmx_file, water_grid, 1)
    # tmx_file.write('  </layer>\n')

    tmx_file.write('  <layer name="low_mountain" width="%i" height="%i" offsetx="0" offsety="-64">\n' % (world.width*3, world.height*3))
    draw_level(world, tmx_file, water_grid, 2)
    tmx_file.write('  </layer>\n')

    # tmx_file.write('  <layer name="low_mountain_water" width="%i" height="%i" offsetx="0" offsety="-64">\n' % (world.width*3, world.height*3))
    # draw_water(world, tmx_file, water_grid, 2)
    # tmx_file.write('  </layer>\n')

    tmx_file.write('  <layer name="med_mountain" width="%i" height="%i" offsetx="0" offsety="-96">\n' % (world.width*3, world.height*3))
    draw_level(world, tmx_file, water_grid, 3)
    tmx_file.write('  </layer>\n')

    # tmx_file.write('  <layer name="med_mountain_water" width="%i" height="%i" offsetx="0" offsety="-96">\n' % (world.width*3, world.height*3))
    # draw_water(world, tmx_file, water_grid, 3)
    # tmx_file.write('  </layer>\n')

    tmx_file.write('  <layer name="high_mountain" width="%i" height="%i" offsetx="0" offsety="-128">\n' % (world.width*3, world.height*3))
    draw_level(world, tmx_file, water_grid, 4)
    tmx_file.write('  </layer>\n')

    # tmx_file.write('  <layer name="high_mountain_water" width="%i" height="%i" offsetx="0" offsety="-128">\n' % (world.width*3, world.height*3))
    # draw_water(world, tmx_file, water_grid, 4)
    # tmx_file.write('  </layer>\n')

    tmx_file.write('  <layer name="forest_ground" width="%i" height="%i" offsetx="0" offsety="0">\n' % (world.width*3, world.height*3))
    draw_forest_level(world, tmx_file, 0)
    tmx_file.write('  </layer>\n')

    tmx_file.write('  <layer name="forest_hill" width="%i" height="%i" offsetx="0" offsety="-32">\n' % (world.width*3, world.height*3))
    draw_forest_level(world, tmx_file, 1)
    tmx_file.write('  </layer>\n')

    tmx_file.write('  <layer name="forest_low_mountain" width="%i" height="%i" offsetx="0" offsety="-64">\n' % (world.width*3, world.height*3))
    draw_forest_level(world, tmx_file, 2)
    tmx_file.write('  </layer>\n')

    tmx_file.write('  <layer name="forest_med_mountain" width="%i" height="%i" offsetx="0" offsety="-96">\n' % (world.width*3, world.height*3))
    draw_forest_level(world, tmx_file, 3)
    tmx_file.write('  </layer>\n')

    tmx_file.write('  <layer name="forest_high_mountain" width="%i" height="%i" offsetx="0" offsety="-128">\n' % (world.width*3, world.height*3))
    draw_forest_level(world, tmx_file, 4)
    tmx_file.write('  </layer>\n')

    tmx_file.write('</map>\n')
    tmx_file.close()
