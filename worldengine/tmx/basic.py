WG_LAND  = 0
WG_OCEAN = 1
WG_RIVER = 2


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
    return [world.river_map[n, w] > 0 or world.is_ocean((w, n)),
            world.river_map[n, x] > 0 or world.is_ocean((x, n)),
            world.river_map[n, e] > 0 or world.is_ocean((e, n)),
            world.river_map[y, w] > 0 or world.is_ocean((w, y)),
            world.river_map[y, e] > 0 or world.is_ocean((e, y)),
            world.river_map[s, w] > 0 or world.is_ocean((w, s)),
            world.river_map[s, x] > 0 or world.is_ocean((x, s)),
            world.river_map[s, e] > 0 or world.is_ocean((e, s))]

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