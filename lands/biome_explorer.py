__author__ = 'Federico Tomassetti'

import sys

from geo import *
from draw import *

# def save(world,i):
#    filename = 'world_%s_elevation_at_%i.png' % (world.name,i)
#    draw_elevation(world,filename)
#    print("+ elevation image generated in '%s'" % filename)

def main():
    if len(sys.argv) != 2:
        usage()
    world_name = sys.argv[1]

    # Load data
    filename = "worlds/world_%s.json" % world_name
    world = World.from_json_file(filename)
    print("+ data loaded from '%s'" % filename)

    #world.temperature['data'] = temperature(seed,world.elevation,mountain_level)

    world.humidity['quantiles']['75'] = find_threshold_f(world.humidity['data'], 0.75, world.ocean)
    world.humidity['quantiles']['50'] = find_threshold_f(world.humidity['data'], 0.50, world.ocean)
    world.humidity['quantiles']['10'] = find_threshold_f(world.humidity['data'], 0.10, world.ocean)

    # Generate images
    filename = 'world_%s_world.png' % world_name
    draw_world(world, filename)
    print("+ world image generated in '%s'" % filename)

    filename = 'world_%s_temperature_levels.png' % world_name
    draw_temperature_levels(world, filename)
    print("+ temperature levels image generated in '%s'" % filename)

    filename = 'world_%s_humidity.png' % world_name
    draw_humidity(world, filename)
    print("+ humidity image generated in '%s'" % filename)


if __name__ == "__main__":
    main()