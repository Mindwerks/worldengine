from biome import Biome, biome_name_to_index

def export_to_tmx(world, tmx_filename):
    tmx_file = open(tmx_filename, "w")
    tmx_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    tmx_file.write('<map version="1.0" orientation="orthogonal" renderorder="right-down" width="%i" height="%i" tilewidth="64" tileheight="64" nextobjectid="1">\n' % (world.width, world.height))
    tmx_file.write('  <tileset firstgid="1" name="biome_tileset" tilewidth="64" tileheight="64" tilecount="%d">\n' % len(Biome.all_names()))
    for biome_name in Biome.all_names():
        index = biome_name_to_index(biome_name)
        tmx_file.write('    <tile id="%i">\n' % index)
        tmx_file.write('       <image width="64" height="64" source="%s.png"/>\n' % biome_name.replace (" ", "_"))
        tmx_file.write('    </tile>\n')
    tmx_file.write('  </tileset>\n')
    tmx_file.write('  <layer name="biome" width="%i" height="%i">\n' % (world.width, world.height))
    tmx_file.write('    <data encoding="csv">\n')
    for y in range(world.height):
        for x in range(world.width):
            biome_name = world.biome[y, x]
            index = biome_name_to_index(biome_name)
            tmx_file.write(str(index + 1))
            if y != (world.height - 1) or (x != world.width - 1):
                tmx_file.write(',')
    tmx_file.write('    </data>\n')
    tmx_file.write('  </layer>\n')
    tmx_file.write('</map>\n')
    tmx_file.close()
