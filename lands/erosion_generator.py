__author__ = 'Federico Tomassetti'

import sys
import random

from lands.geo import World, erode
from lands.draw import draw_elevation


def save(world, i):
    filename = 'world_%s_elevation_at_%i.png' % (world.name, i)
    draw_elevation(world, filename)
    print("+ elevation image generated in '%s'" % filename)


def main():
    if len(sys.argv) != 3:
        usage()
    world_name = sys.argv[1]
    drops = int(sys.argv[2])
    random.seed()
    seed = random.randint(0, 65536)
    print('Using seed %i to add rivers & erosion to world "%s". Drops=%i' % (seed, world_name, drops))

    # Load data
    filename = "worlds/world_%s.json" % world_name
    world = World.from_json_file(filename)
    print("+ data loaded from '%s'" % filename)

    _watermap = None
    for i in xrange(20):
        filename = 'world_%s_%i_elevation.png' % (world_name, i)
        draw_elevation(world, filename)
        # filename = 'world_%s_%i_noshadow_elevation.png' % (world_name,i)
        #draw_elevation(world,filename,shadow=False)
        erode(world, 500000)

        # Generate images
        #filename = 'world_%s_elevation.png' % world_name
        #draw_elevation(world,filename)
        #print("+ elevation image generated in '%s'" % filename)

        # Generate images
        #filename = 'world_%s_biome.png' % world_name
        #draw_biome(w.biome,filename)
        #print("+ biome image generated in '%s'" % filename)


def usage():
    print ' -------------------------------------------------------------------------'
    print ' Federico Tomassetti, 2013'
    print ' World water generator'
    print ' '
    print ' water generator <world_name> <drops>'
    print ' -------------------------------------------------------------------------'
    sys.exit(' ')

# -------------------------------
if __name__ == "__main__":
    main()