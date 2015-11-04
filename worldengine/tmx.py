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


def export_to_tmx(world, tmx_filename):
    tmx_file = open(tmx_filename, "w")
    tmx_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    tmx_file.write('<map version="1.0" orientation="orthogonal" renderorder="right-down" width="%i" height="%i" tilewidth="64" tileheight="64" nextobjectid="1">\n' % (world.width, world.height))
    tmx_file.write('  <tileset firstgid="1" name="biome_tileset" tilewidth="64" tileheight="64" tilecount="%d">\n' % len(Biome.all_names()))

    tmx_file.write('    <tile id="0">\n')
    tmx_file.write('       <image width="64" height="64" source="ocean.png"/>\n')
    tmx_file.write('    </tile>\n')
    tmx_file.write('    <tile id="1">\n')
    tmx_file.write('       <image width="64" height="64" source="mountain.png"/>\n')
    tmx_file.write('    </tile>\n')
    tmx_file.write('    <tile id="2">\n')
    tmx_file.write('       <image width="64" height="64" source="river.png"/>\n')
    tmx_file.write('    </tile>\n')
    tmx_file.write('    <tile id="3">\n')
    tmx_file.write('       <image width="64" height="64" source="desert.png"/>\n')
    tmx_file.write('    </tile>\n')
    tmx_file.write('    <tile id="4">\n')
    tmx_file.write('       <image width="64" height="64" source="forest.png"/>\n')
    tmx_file.write('    </tile>\n')
    tmx_file.write('    <tile id="5">\n')
    tmx_file.write('       <image width="64" height="64" source="jungle.png"/>\n')
    tmx_file.write('    </tile>\n')
    tmx_file.write('    <tile id="6">\n')
    tmx_file.write('       <image width="64" height="64" source="plain.png"/>\n')
    tmx_file.write('    </tile>\n')
    tmx_file.write('    <tile id="7">\n')
    tmx_file.write('       <image width="64" height="64" source="iceland.png"/>\n')
    tmx_file.write('    </tile>\n')

    tmx_file.write('  </tileset>\n')
    tmx_file.write('  <layer name="biome" width="%i" height="%i">\n' % (world.width, world.height))
    tmx_file.write('    <data encoding="csv">\n')

    unkwown = sets.Set()
    for y in range(world.height):
        for x in range(world.width):
            biome_name = world.biome[y, x]
            pos = (x, y)
            if world.is_ocean(pos):
                index = 1
            elif world.is_mountain(pos):
                index = 2
            elif world.river_map[x, y] > 0:
                index = 3
            elif biome_name=='subtropical desert' or biome_name=='tropical desert' or biome_name=='tropical desert scrub' or biome_name=='subtropical desert scrub':
                index = 4
            elif biome_name=='cool temperate moist forest' or biome_name=='cool temperate rain forest' or biome_name=='warm temperate dry forest':
                index = 5
            elif biome_name=='subtropical moist forest' or biome_name=='subtropical rain forest' or biome_name=='subtropical wet forest':
                index = 6
            elif biome_name=='boreal desert' or biome_name=='polar desert' or biome_name=='ice':
                index = 8
            else:
                index = 7
                if not biome_name in unkwown:
                    unkwown.add(biome_name)
                    print(biome_name)
            tmx_file.write(str(index))
            if y != (world.height - 1) or (x != world.width - 1):
                tmx_file.write(',')
    tmx_file.write('    </data>\n')
    tmx_file.write('  </layer>\n')
    tmx_file.write('</map>\n')
    tmx_file.close()
