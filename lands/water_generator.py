__author__ = 'Federico Tomassetti'

import sys


from lands.geo import World, find_threshold, find_threshold_f
from lands.draw import draw_watermap


def save(world, i):
    filename = 'world_%s_elevation_at_%i.png' % (world.name, i)
    draw_elevation(world, filename)
    print("+ elevation image generated in '%s'" % filename)


def main():
    if len(sys.argv) != 2:
        usage()
    world_name = sys.argv[1]
    print('Add rivers & erosion to world "%s"' % (world_name))

    # Load data
    filename = "worlds/world_%s.json" % world_name
    world = World.from_json_file(filename)
    print("+ data loaded from '%s'" % filename)

    # torrent
    th = find_threshold_f(world.watermap, 0.05, ocean=world.ocean)
    filename = 'world_%s_watermap5.png' % world_name
    draw_watermap(world, filename, th)

    # rivers
    th = find_threshold(world.watermap, 0.02, ocean=world.ocean)
    filename = 'world_%s_watermap2.png' % world_name
    draw_watermap(world, filename, th)

    # main rivers
    th = find_threshold(world.watermap, 0.007, ocean=world.ocean)
    filename = 'world_%s_watermap07.png' % world_name
    draw_watermap(world, filename, th)

    # Generate images
    # filename = 'world_%s_elevation.png' % world_name
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