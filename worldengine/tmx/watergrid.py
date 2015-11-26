import numpy
from basic import *


def _water_cell_grid(world, pos):
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


def _clean_water_grid(water_grid):

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
            cell = _water_cell_grid(world, pos)
            for dy in range(3):
                for dx in range(3):
                    water_grid[x * 3 + dx, y * 3 + dy] = cell[dy][dx]

    _clean_water_grid(water_grid)
    return water_grid


