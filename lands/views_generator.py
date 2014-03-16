import sys
import random
import jsonpickle

from geo import world_gen, World, antialias, erode, watermap, find_threshold, irrigation, humidity, find_threshold_f
from draw import draw_watermap, draw_elevation, draw_irrigation, draw_humidity, draw_biome

def save(world,i):
    filename = 'world_%s_elevation_at_%i.png' % (world.name,i)
    draw_elevation(world,filename)
    print("+ elevation image generated in '%s'" % filename)


def main():
    if len(sys.argv)!=2:
        usage()
    world_name = sys.argv[1]    

    # Load data
    filename = "worlds/world_%s.json" % world_name
    world = World.from_json_file(filename)
    print("+ data loaded from '%s'" % filename)

    filename = 'world_%s_biome.png' % (world_name)
    draw_biome(world.biome,filename)
    print("+ biome image generated in '%s'" % filename)

    filename = 'world_%s_irrigation.png' % (world_name)
    draw_irrigation(world,filename)
    print("+ irrigation image generated in '%s'" % filename)

    filename = 'world_%s_humidity.png' % (world_name)
    draw_humidity(world,filename)
    print("+ humidity image generated in '%s'" % filename)

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

#-------------------------------
if __name__ == "__main__":
    main()