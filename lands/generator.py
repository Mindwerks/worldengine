import sys
import random
import pickle

from geo import world_gen
from draw import draw_biome
import geo
import draw
from optparse import OptionParser

OPERATIONS = 'world|plates'

def generate_world(seed,world_name,output_dir):
    w = world_gen(world_name,seed,verbose=True)

    # Save data
    filename = "%s/world_%s.world" % (output_dir,world_name)
    with open(filename, "w") as f:
        pickle.dump(w, f, pickle.HIGHEST_PROTOCOL)
    print("+ data saved in '%s'" % filename)

    # Generate images
    filename = '%s/world_%s_ocean.png' % (output_dir,world_name)
    draw.draw_ocean(w.ocean,filename)
    
    filename = '%s/world_%s_biome.png' % (output_dir,world_name)
    draw_biome(w.biome,filename)
    print("+ biome image generated in '%s'" % filename)
    filename = '%s/world_elevation_%s.png' % (output_dir,world_name)
    e_as_array = []
    for y in xrange(512):
        for x in xrange(512):
            e_as_array.append(w.elevation['data'][y][x])
    draw.draw_simple_elevation(e_as_array,filename)  

def generate_plates(seed, world_name,output_dir):
    plates = geo.generate_plates_simulation(seed)

    # Generate images
    filename = '%s/plates_%s.png' % (output_dir,world_name)
    draw.draw_simple_elevation(plates,filename)
    print("+ plates image generated in '%s'" % filename)
    plates = geo.center_elevation_map(plates,512,512)
    filename = '%s/centered_plates_%s.png' % (output_dir,world_name)
    draw.draw_simple_elevation(plates,filename)    
    print("+ centered plates image generated in '%s'" % filename)


def main():

    parser = OptionParser()
    parser.add_option('-o', '--output', dest='output_dir',help="generate files in OUTPUT",metavar="FILE",default='.')
    parser.add_option('-s', '--seed', dest='seed',help="use SEED to initialize the pseudo-random generation",metavar="SEED",)
    (options,args) = parser.parse_args()

    if len(args)<1 or len(args)>2:
        usage()
    world_name = args[0]        
    if len(args)>=2:
        operation = args[1]
    else:
        operation = 'world'
    random.seed()
    if options.seed:
        seed = int(options.seed)
    else:
        seed = random.randint(0,65536)
    print('World generator')
    print(' seed      : %i' % seed)
    print(' name      : %s' % world_name)
    print(' operation : %s generation' % operation)
    if operation=='world':
        generate_world(seed,world_name,options.output_dir)
    elif operation=='plates':
        generate_plates(seed,world_name,options.output_dir)
    else:
        raise Exception('Unknown operation: valid operations are %s' % OPERATIONS)

def usage():
    print ' -------------------------------------------------------------------------'
    print ' Federico Tomassetti, 2013'
    print ' World generator'
    print ' '
    print ' generator <world_name> [operation] [options]'
    print ' possible operations: %s' % OPERATIONS
    print ' use -h to see options'
    print ' -------------------------------------------------------------------------'
    sys.exit(' ')

#-------------------------------
if __name__ == "__main__":
    main()