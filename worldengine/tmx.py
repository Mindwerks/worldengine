from biome import Biome, biome_name_to_index
import sets

class Tiles:
    ocean = 1
    mountain = 2
    river = 3
    desert = 4
    forest = 5
    jungle = 6
    plain = 7
    iceland = 8

# 260,261,281,282,301,302,303,322,324,343,344,345,366,244

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



                    # around = get_land_around(world,x,y)
                    # if around == [False, False, False, False, True, False, True, True] \
                    #         or around == [False, False, True, False, True, False, True, True] \
                    #         or around == [False, False, False, False, True, True, True, True] \
                    #         or around == [False, False, True, False, True, True, True, True]:
                    #     index = TLAND_E_S_SE
                    # elif around == [False, False, False, True, False, True, True, False] \
                    #         or around == [True, False, False, True, False, True, True, False] \
                    #         or around == [False, False, False, True, False, True, True, True] \
                    #         or around == [True, False, False, True, False, True, True, True]:
                    #     index = TLAND_W_SW_S
                    # elif around == [False, True, True, False, True, False, False, False] \
                    #         or around == [True, True, True, False, True, False, False, False] \
                    #         or around == [False, True, True, False, True, False, False, True] \
                    #         or around == [True, True, True, False, True, False, False, True]:
                    #     index = TLAND_N_NE_E
                    # elif around == [True, True, False, True, False, False, False, False] \
                    #         or around == [True, True, True, True, False, False, False, False] \
                    #         or around == [True, True, False, True, False, True, False, False] \
                    #         or around == [True, True, True, True, False, True, False, False]:
                    #     index = TLAND_NW_N_W
                    # elif around == [True, True, False, True, True, True, True, True]:
                    #     index = TLAND_BUT_NE
                    # elif around == [False, True, True, True, True, True, True, True]:
                    #     index = TLAND_BUT_NW
                    # elif around == [True, True, True, True, True, True, True, False]:
                    #     index = TLAND_BUT_SE
                    # elif around == [True, True, True, True, True, False, True, True]:
                    #     index = TLAND_BUT_SW
                    # elif around[0] and around[1] and around[2] and around[3] and around[4] and not around[6]:
                    #     index = TLAND_COAST_N
                    # elif around[5] and around[6] and around[7] and around[3] and around[4] and not around[1]:
                    #     index = TLAND_COAST_S
                    # elif around[0] and around[1] and around[3] and around[5] and around[6] and not around[4]:
                    #     index = TLAND_COAST_W
                    # elif around[1] and around[2] and around[4] and around[6] and around[7] and not around[3]:
                    #     index = TLAND_COAST_E
                    # elif not around[1] and not around[3] and not around[4] and not around[6]:
                    #     index = T_ISLAND
                    # else:
                    #     index = TLAND


                # biome_name = world.biome[y, x]
                # pos = (x, y)
                # if world.is_ocean(pos):
                #     index = 1
                # elif world.is_mountain(pos):
                #     index = 2
                # elif world.river_map[x, y] > 0:
                #     index = 3
                # elif biome_name=='subtropical desert' or biome_name=='tropical desert' or biome_name=='tropical desert scrub' or biome_name=='subtropical desert scrub':
                #     index = 4
                # elif biome_name=='cool temperate moist forest' or biome_name=='cool temperate rain forest' or biome_name=='warm temperate dry forest':
                #     index = 5
                # elif biome_name=='subtropical moist forest' or biome_name=='subtropical rain forest' or biome_name=='subtropical wet forest':
                #     index = 6
                # elif biome_name=='boreal desert' or biome_name=='polar desert' or biome_name=='ice':
                #     index = 8
                # else:
                #     index = 7
                #     if not biome_name in unkwown:
                #         unkwown.add(biome_name)
                #         print(biome_name)


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


def export_to_tmx(world, tmx_filename):
    _transform_for_tmx(world)

    tmx_file = open(tmx_filename, "w")
    tmx_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    tmx_file.write('<map version="1.0" orientation="orthogonal" renderorder="right-down" width="%i" height="%i" tilewidth="32" tileheight="32" nextobjectid="1">\n' % (world.width*3, world.height*3))
    tmx_file.write('<tileset firstgid="1" name="T2" tilewidth="32" tileheight="32" tilecount="483">\n')
    tmx_file.write('<image source="terrain_2.png" width="672" height="736"/>\n')
    tmx_file.write('</tileset>\n')

    # tmx_file.write('<map version="1.0" orientation="orthogonal" renderorder="right-down" width="%i" height="%i" tilewidth="64" tileheight="64" nextobjectid="1">\n' % (world.width, world.height))
    # tmx_file.write('  <tileset firstgid="1" name="biome_tileset" tilewidth="64" tileheight="64" tilecount="%d">\n' % len(Biome.all_names()))
    #
    # tmx_file.write('    <tile id="0">\n')
    # tmx_file.write('       <image width="64" height="64" source="ocean.png"/>\n')
    # tmx_file.write('    </tile>\n')
    # tmx_file.write('    <tile id="1">\n')
    # tmx_file.write('       <image width="64" height="64" source="mountain.png"/>\n')
    # tmx_file.write('    </tile>\n')
    # tmx_file.write('    <tile id="2">\n')
    # tmx_file.write('       <image width="64" height="64" source="river.png"/>\n')
    # tmx_file.write('    </tile>\n')
    # tmx_file.write('    <tile id="3">\n')
    # tmx_file.write('       <image width="64" height="64" source="desert.png"/>\n')
    # tmx_file.write('    </tile>\n')
    # tmx_file.write('    <tile id="4">\n')
    # tmx_file.write('       <image width="64" height="64" source="forest.png"/>\n')
    # tmx_file.write('    </tile>\n')
    # tmx_file.write('    <tile id="5">\n')
    # tmx_file.write('       <image width="64" height="64" source="jungle.png"/>\n')
    # tmx_file.write('    </tile>\n')
    # tmx_file.write('    <tile id="6">\n')
    # tmx_file.write('       <image width="64" height="64" source="plain.png"/>\n')
    # tmx_file.write('    </tile>\n')
    # tmx_file.write('    <tile id="7">\n')
    # tmx_file.write('       <image width="64" height="64" source="iceland.png"/>\n')
    # tmx_file.write('    </tile>\n')
    #
    # tmx_file.write('  </tileset>\n')
    tmx_file.write('  <layer name="biome" width="%i" height="%i">\n' % (world.width*3, world.height*3))
    tmx_file.write('    <data encoding="csv">\n')

    unkwown = sets.Set()
    for y in range(world.height):
        for dy in range(3):
            for x in range(world.width):
                pos = (x, y)
                if world.is_ocean(pos):
                    indexes = [TOCEAN, TOCEAN, TOCEAN]
                elif world.river_map[x, y] > 0:
                    ocean_around = [(not v) for v in get_land_around(world,x,y)]
                    around = get_river_around(world,x,y)
                    if not around[1] and not around[3] and not around[4] and around[6]:
                        # north source
                        if dy == 0:
                            indexes = [TLAND_BUT_SE, TLAND_COAST_N, TLAND_BUT_SW]
                        elif dy == 1:
                            indexes = [TLAND_COAST_W, TRIVER, TLAND_COAST_E]
                        else:
                            indexes = [TLAND_COAST_W, TRIVER, TLAND_COAST_E]
                            if ocean_around[6]:
                                indexes[0] = TLAND_NW_N_W
                                indexes[2] = TLAND_N_NE_E
                    elif around[1] and not around[3] and not around[4] and not around[6]:
                        # south source
                        if dy == 0:
                            indexes = [TLAND_COAST_W, TRIVER, TLAND_COAST_E]
                            if ocean_around[1]:
                                indexes[0] = TLAND_W_SW_S
                                indexes[2] = TLAND_E_S_SE
                            if ocean_around[2]:
                                indexes[2] = TLAND_E_S_SE
                        elif dy == 1:
                            indexes = [TLAND_COAST_W, TRIVER, TLAND_COAST_E]
                        else:
                            indexes = [TLAND_BUT_NE, TLAND_COAST_S, TLAND_BUT_NW]
                    elif not around[1] and around[3] and not around[4] and not around[6]:
                        # east source
                        if dy == 0:
                            indexes = [TLAND_COAST_N, TLAND_COAST_N, TLAND_BUT_SW]
                            if ocean_around[3]:
                                indexes[0] = TLAND_N_NE_E
                            if ocean_around[1]:
                                indexes = [TOCEAN,TOCEAN,TOCEAN]
                        elif dy == 1:
                            indexes = [TRIVER, TRIVER, TLAND_COAST_E]
                            if ocean_around[1]:
                                indexes[2] = TOCEAN
                        else:
                            indexes = [TLAND_COAST_S, TLAND_COAST_S, TLAND_BUT_NW]
                            if ocean_around[3]:
                                indexes[0] = TLAND_E_S_SE
                            if ocean_around[4]:
                                indexes[2] = TLAND_W_SW_S
                    elif not around[1] and not around[3] and around[4] and not around[6]:
                        # west source
                        if dy == 0:
                            indexes = [TLAND_BUT_SE, TLAND_COAST_N, TLAND_COAST_N]
                            if ocean_around[4]:
                                indexes[2] = TLAND_NW_N_W
                        elif dy == 1:
                            indexes = [TLAND_COAST_W, TRIVER, TRIVER]
                        else:
                            indexes = [TLAND_BUT_NE, TLAND_COAST_S, TLAND_COAST_S]
                            if ocean_around[4]:
                                indexes[2] = TLAND_W_SW_S
                    elif not around[1] and around[3] and around[4] and around[6]:
                        # triangle to south
                        if dy == 0:
                            indexes = [TLAND_COAST_N, TLAND_COAST_N, TLAND_COAST_N]
                            if ocean_around[4]:
                                indexes[2] = TLAND_NW_N_W
                        elif dy == 1:
                            indexes = [TRIVER, TRIVER, TRIVER]
                        else:
                            indexes = [TLAND_W_SW_S, TRIVER, TLAND_E_S_SE]
                            if around[5]:
                                indexes[0] = TRIVER
                            if around[7]:
                                indexes[2] = TRIVER
                            if ocean_around[4]:
                                indexes[2] = TOCEAN
                    elif around[1] and around[3] and around[4] and not around[6]:
                        # triangle to north
                        if dy == 0:
                            indexes = [TLAND_NW_N_W, TRIVER, TLAND_N_NE_E]
                        elif dy == 1:
                            indexes = [TRIVER, TRIVER, TRIVER]
                        else:
                            indexes = [TLAND_COAST_S, TLAND_COAST_S, TLAND_COAST_S]
                            if ocean_around[5]:
                                indexes[0] = TLAND_E_S_SE
                    elif around[1] and around[3] and not around[4] and around[6]:
                        # triangle to west
                        if dy == 0:
                            indexes = [TLAND_NW_N_W, TRIVER, TLAND_COAST_E]
                            if around[2]:
                                indexes[2] = TLAND_E_S_SE
                            if ocean_around[3]:
                                indexes[0] = TOCEAN
                        elif dy == 1:
                            indexes = [TRIVER, TRIVER, TLAND_COAST_E]
                        else:
                            indexes = [TLAND_W_SW_S, TRIVER, TLAND_COAST_E]
                            if around[7]:
                                indexes[2] = TLAND_N_NE_E
                            if ocean_around[6]:
                                indexes[2] = TLAND_N_NE_E
                            if ocean_around[3]:
                                indexes[0] = TOCEAN
                    elif around[1] and not around[3] and around[4] and around[6]:
                        # triangle to east
                        if dy == 0:
                            indexes = [TLAND_COAST_W, TRIVER, TLAND_N_NE_E]
                        elif dy == 1:
                            indexes = [TLAND_COAST_W, TRIVER, TRIVER]
                        else:
                            indexes = [TLAND_COAST_W, TRIVER, TLAND_E_S_SE]
                    elif around[1] and not around[3] and not around[4] and around[6]:
                        #vertical pipe
                        if dy == 0:
                            indexes = [TLAND_COAST_W, TRIVER, TLAND_COAST_E]
                            if ocean_around[0]:
                                indexes[0] = TLAND_W_SW_S
                            if ocean_around[1]:
                                indexes[2] = TLAND_E_S_SE
                            if ocean_around[3]:
                                indexes[0] = TOCEAN
                        elif dy == 1:
                            indexes = [TLAND_COAST_W, TRIVER, TLAND_COAST_E]
                            if ocean_around[3]:
                                indexes[0] = TOCEAN
                        else:
                            indexes = [TLAND_COAST_W, TRIVER, TLAND_COAST_E]
                            if ocean_around[6]:
                                indexes[0] = TLAND_NW_N_W
                                indexes[2] = TLAND_N_NE_E
                            if ocean_around[3]:
                                indexes[0] = TOCEAN
                    elif not around[1] and around[3] and around[4] and not around[6]:
                        #horizontal pipe
                        if dy == 0:
                            indexes = [TLAND_COAST_N, TLAND_COAST_N, TLAND_COAST_N]
                            if ocean_around[0]:
                                indexes[0] = TLAND_N_NE_E
                            if ocean_around[3]:
                                indexes[0] = TLAND_N_NE_E
                            if ocean_around[1]:
                                indexes[0] = TOCEAN
                                indexes[1] = TOCEAN
                                indexes[2] = TOCEAN
                        elif dy == 1:
                            indexes = [TRIVER, TRIVER, TRIVER]
                        else:
                            indexes = [TLAND_COAST_S, TLAND_COAST_S, TLAND_COAST_S]
                            if ocean_around[3]:
                                indexes[0] = TLAND_E_S_SE
                    elif around[1] and not around[3] and around[4] and not around[6]:
                        #curve n -> e
                        if dy == 0:
                            indexes = [TLAND_COAST_W, TRIVER, TLAND_N_NE_E]
                            if ocean_around[4]:
                                indexes[2] = TOCEAN
                        elif dy == 1:
                            indexes = [TLAND_COAST_W, TRIVER, TRIVER]
                        else:
                            indexes = [TLAND_BUT_NE, TLAND_COAST_S, TLAND_COAST_S]
                            if ocean_around[4]:
                                indexes[2] = TLAND_W_SW_S
                    elif around[1] and around[3] and not around[4] and not around[6]:
                        #curve n -> w
                        if dy == 0:
                            indexes = [TLAND_NW_N_W, TRIVER, TLAND_COAST_E]
                        elif dy == 1:
                            indexes = [TRIVER, TRIVER, TLAND_COAST_E]
                        else:
                            indexes = [TLAND_COAST_S, TLAND_COAST_S, TLAND_BUT_NW]
                    elif not around[1] and around[3] and not around[4] and around[6]:
                        #curve w -> s
                        if dy == 0:
                            indexes = [TLAND_COAST_N, TLAND_COAST_N, TLAND_BUT_SW]
                        elif dy == 1:
                            indexes = [TRIVER, TRIVER, TLAND_COAST_E]
                        else:
                            indexes = [TLAND_W_SW_S, TRIVER, TLAND_COAST_E]
                            if ocean_around[5]:
                                indexes[0] = TOCEAN
                            if ocean_around[6]:
                                indexes[2] = TLAND_N_NE_E
                            if ocean_around[7]:
                                indexes[2] = TLAND_N_NE_E
                    elif not around[1] and not around[3] and around[4] and around[6]:
                        #curve e -> s
                        if dy == 0:
                            indexes = [TLAND_BUT_SE, TLAND_COAST_N, TLAND_COAST_N]
                        elif dy == 1:
                            indexes = [TLAND_COAST_W, TRIVER, TRIVER]
                        else:
                            indexes = [TLAND_COAST_W, TRIVER, TLAND_E_S_SE]
                            #if around[7]:
                            #    indexes[2] = TRIVER
                            if ocean_around[6]:
                                indexes[0] = TLAND_NW_N_W
                                indexes[2] = TOCEAN
                    else:
                        if dy == 0:
                            indexes = [TRIVER, TRIVER, TRIVER]
                        elif dy == 1:
                            indexes = [TRIVER, TRIVER, TRIVER]
                        else:
                            indexes = [TRIVER, TRIVER, TRIVER]
                else:
                    around = get_land_around(world,x,y)
                    if not around[1] and not around[3] and not around[4] and not around[6]:
                        # island
                        if dy == 0:
                            indexes = [TLAND_E_S_SE, TLAND_COAST_S, TLAND_W_SW_S]
                        elif dy == 1:
                            indexes = [TLAND_COAST_E, TLAND, TLAND_COAST_W]
                        else:
                            indexes = [TLAND_N_NE_E, TLAND_COAST_N, TLAND_NW_N_W]
                    elif not around[1] and not around[3] and around[4] and around[6] and around[7]:
                        # land at E and S (and in corner), water at N and W
                        if dy == 0:
                            indexes = [TOCEAN, TLAND_E_S_SE, TLAND_COAST_S]
                        elif dy == 1:
                            indexes = [TLAND_E_S_SE, TLAND_BUT_NW, TLAND]
                        else:
                            indexes = [TLAND_COAST_E, TLAND, TLAND]
                    elif not around[1] and around[3] and not around[4] and around[6] and around[5]:
                        # land at W and S (and in corner), water at N and E
                        if dy == 0:
                            indexes = [TLAND_COAST_S, TLAND_W_SW_S, TOCEAN]
                        elif dy == 1:
                            indexes = [TLAND, TLAND_BUT_NE, TLAND_W_SW_S]
                        else:
                            indexes = [TLAND, TLAND, TLAND_COAST_W]
                    elif not around[1] and around[3] and around[4] and around[6]:
                        # Coast south
                        if dy == 0:
                            indexes = [TLAND_COAST_S, TLAND_COAST_S, TLAND_COAST_S]
                        elif dy == 1:
                            indexes = [TLAND, TLAND, TLAND]
                        else:
                            indexes = [TLAND, TLAND, TLAND]
                            if not around[5]:
                                indexes[0] = TLAND_BUT_SW
                            if not around[7]:
                                indexes[2] = TLAND_BUT_SE
                    elif around[1] and around[3] and around[4] and not around[6]:
                        # Coast north
                        if dy == 0:
                            indexes = [TLAND, TLAND, TLAND]
                            if not around[0]:
                                indexes[0] = TLAND_BUT_NW
                            if not around[2]:
                                indexes[2] = TLAND_BUT_NE
                        elif dy == 1:
                            indexes = [TLAND, TLAND, TLAND]
                        else:
                            indexes = [TLAND_COAST_N, TLAND_COAST_N, TLAND_COAST_N]
                    elif around[1] and around[3] and not around[4] and around[6]:
                        # Coast west
                        if dy == 0:
                            indexes = [TLAND, TLAND, TLAND_COAST_W]
                            if not around[0]:
                                indexes[0] = TLAND_BUT_NW
                        elif dy == 1:
                            indexes = [TLAND, TLAND, TLAND_COAST_W]
                        else:
                            indexes = [TLAND, TLAND, TLAND_COAST_W]
                            if not around[5]:
                                indexes[0] = TLAND_BUT_SW
                    elif around[1] and around[4] and around[6] and not around[3]:
                        # Coast east
                        if dy == 0:
                            indexes = [TLAND_COAST_E, TLAND, TLAND]
                            if not around[2]:
                                indexes[2] = TLAND_BUT_NE
                        elif dy == 1:
                            indexes = [TLAND_COAST_E, TLAND, TLAND]
                        else:
                            indexes = [TLAND_COAST_E, TLAND, TLAND]
                            if not around[7]:
                                indexes[2] = TLAND_BUT_SE
                    elif around[1] and around[3] and not around[4] and not around[6]:
                        # Land is North and West
                        if dy == 0:
                            indexes = [TLAND, TLAND, TLAND_COAST_W]
                            if not around[0]:
                                indexes[0] = TLAND_BUT_NW
                        elif dy == 1:
                            indexes = [TLAND, TLAND_BUT_SE, TLAND_NW_N_W]
                        else:
                            indexes = [TLAND_COAST_N, TLAND_NW_N_W, TOCEAN]
                    elif around[1] and not around[3] and around[4] and not around[6]:
                        # Land is North and East
                        if dy == 0:
                            indexes = [TLAND_COAST_E, TLAND, TLAND]
                        elif dy == 1:
                            indexes = [TLAND_N_NE_E, TLAND_BUT_SW, TLAND]
                        else:
                            indexes = [TOCEAN, TLAND_N_NE_E, TLAND_COAST_N]
                    elif not around[1] and around[3] and not around[4] and around[6]:
                        # Land is South and West
                        if dy == 0:
                            indexes = [TLAND_COAST_S, TLAND_W_SW_S, TOCEAN]
                        elif dy == 1:
                            indexes = [TLAND, TLAND_BUT_NE, TLAND_W_SW_S]
                        else:
                            indexes = [TLAND, TLAND, TLAND_COAST_W]
                            if not around[5]:
                                indexes[0] = TLAND_BUT_SW
                    elif not around[1] and not around[3] and around[4] and around[6]:
                        # Land is South and East
                        if dy == 0:
                            indexes = [TOCEAN, TLAND_E_S_SE, TLAND_COAST_S]
                        elif dy == 1:
                            indexes = [TLAND_E_S_SE, TLAND_BUT_NW, TLAND]
                        else:
                            indexes = [TLAND_COAST_E, TLAND, TLAND]
                            if not around[7]:
                                indexes[2] = TLAND_BUT_SE
                    elif not around[1] and around[3] and not around[4] and not around[6]:
                        # Peninsula going east
                        if dy == 0:
                            indexes = [TLAND_W_SW_S, TOCEAN, TOCEAN]
                        elif dy == 1:
                            indexes = [TLAND_COAST_W, TOCEAN, TOCEAN]
                        else:
                            indexes = [TLAND_NW_N_W, TOCEAN, TOCEAN]
                    elif not around[1] and not around[3] and around[4] and not around[6]:
                        # Peninsula going west
                        if dy == 0:
                            indexes = [TOCEAN, TOCEAN, TLAND_E_S_SE]
                        elif dy == 1:
                            indexes = [TOCEAN, TOCEAN, TLAND_COAST_E]
                        else:
                            indexes = [TOCEAN, TOCEAN, TLAND_N_NE_E]
                    elif around[1] and not around[3] and not around[4] and not around[6]:
                        # Peninsula going south
                        if dy == 0:
                            indexes = [TLAND_N_NE_E, TLAND_COAST_N, TLAND_NW_N_W]
                        elif dy == 1:
                            indexes = [TOCEAN, TOCEAN, TOCEAN]
                        else:
                            indexes = [TOCEAN, TOCEAN, TOCEAN]
                    elif not around[1] and not around[3] and not around[4] and around[6]:
                        # Peninsula going north
                        if dy == 0:
                            indexes = [TOCEAN, TOCEAN, TOCEAN]
                        elif dy == 1:
                            indexes = [TOCEAN, TOCEAN, TOCEAN]
                        else:
                            indexes = [TLAND_E_S_SE, TLAND_COAST_S, TLAND_W_SW_S]
                    elif not around[1] and around[3] and around[4] and not around[6]:
                        # Horizontal bridge
                        if dy == 0:
                            indexes = [TLAND_COAST_S, TLAND_COAST_S, TLAND_COAST_S]
                        elif dy == 1:
                            indexes = [TLAND, TLAND, TLAND]
                        else:
                            indexes = [TLAND_COAST_N, TLAND_COAST_N, TLAND_COAST_N]
                    elif around[1] and not around[3] and not around[4] and around[6]:
                        # Vertical bridge
                        if dy == 0:
                            indexes = [TLAND_COAST_E, TLAND, TLAND_COAST_W]
                        elif dy == 1:
                            indexes = [TLAND_COAST_E, TLAND, TLAND_COAST_W]
                        else:
                            indexes = [TLAND_COAST_E, TLAND, TLAND_COAST_W]
                    elif around[1] and around[3] and around[4] and around[6]:
                        # This could have just water in diagonal. In that case it needs to use a different
                        # tile in the corner
                        if dy == 0:
                            first_cell = TLAND
                            last_cell = TLAND
                            if not around[0]:
                                first_cell = TLAND_BUT_NW
                            if not around[2]:
                                last_cell = TLAND_BUT_NE
                            indexes = [first_cell, TLAND, last_cell]
                        elif dy == 1:
                            indexes = [TLAND, TLAND, TLAND]
                        elif dy == 2:
                            first_cell = TLAND
                            last_cell = TLAND
                            if not around[5]:
                                first_cell = TLAND_BUT_SW
                            if not around[7]:
                                last_cell = TLAND_BUT_SE
                            indexes = [first_cell, TLAND, last_cell]
                    elif around==[True,True,True,True,True,True,True,True]:
                        indexes = [TLAND, TLAND, TLAND]
                    else:
                        raise Exception(str(around))
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
