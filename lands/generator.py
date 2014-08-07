import sys
import random
import pickle

from geo import world_gen
from draw import draw_biome, draw_precipitation
import geo
import draw
from optparse import OptionParser
import os

OPERATIONS = 'world|plates'

def generate_world(seed, world_name, output_dir, width, height, step):
    w = world_gen(world_name, seed, True, width, height, step)

    print('') # empty line
    print('Producing ouput:')

    # Save data
    filename = "%s/%s.world" % (output_dir,world_name)
    with open(filename, "w") as f:
        pickle.dump(w, f, pickle.HIGHEST_PROTOCOL)
    print("* world data saved in '%s'" % filename)

    # Generate images
    filename = '%s/%s_ocean.png' % (output_dir,world_name)
    draw.draw_ocean(w.ocean,filename)
    print("* ocean image generated in '%s'" % filename)

    if step.include_precipitations:
        filename = '%s/%s_precipitations.png' % (output_dir,world_name)
        draw_precipitation(w.precipitation['data'],filename)
        print("* precipitations image generated in '%s'" % filename)
    
    if step.include_biome:
        filename = '%s/%s_biome.png' % (output_dir,world_name)
        draw_biome(w.biome,filename)
        print("* biome image generated in '%s'" % filename)
    
    filename = '%s/%s_elevation.png' % (output_dir,world_name)
    e_as_array = []
    for y in xrange(512):
        for x in xrange(512):
            e_as_array.append(w.elevation['data'][y][x])
    draw.draw_simple_elevation(e_as_array,filename)  
    print("* elevation image generated in '%s'" % filename)
    

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

class Step:

    def __init__(self, name):
        self.name = name
        self.include_plates = True
        self.include_precipitations = False
        self.include_erosion = False
        self.include_biome = False

    @staticmethod
    def get_by_name(name):
        step = None
        if name=="plates":
            step = Step(name)
        elif name=="precipitations":
            step = Step(name)
            step.include_precipitations = True
        elif name=="full":
            step = Step(name)
            step.include_precipitations = True
            step.include_erosion = True
            step.include_biome = True

        return step


def check_step(step_name):
    step = Step.get_by_name(step_name)
    if step==None:
        print("ERROR: unknown step name, using default 'full'")
        return Step.get_by_name("full")
    else:
        return step

def main():
    parser = OptionParser()
    parser.add_option('-o', '--output', dest='output_dir', help="generate files in OUTPUT", metavar="FILE", default='.')
    parser.add_option('-n', '--worldname', dest='worldname', help="set WORLDNAME", metavar="WORLDNAME")
    parser.add_option('-s', '--seed', dest='seed', help="use SEED to initialize the pseudo-random generation", metavar="SEED")
    parser.add_option('-t', '--step', dest='step', help="use STEP to specify how far to proceed in the world generation process", metavar="STEP")    
    (options,args) = parser.parse_args()

    if not os.path.isdir(options.output_dir):
        raise Exception("Output dir does not exist or it is not a dir")

    if len(args)>2:
        usage()    
    if len(args)>=2:
        operation = args[1]
    else:
        operation = 'world'
    random.seed()
    if options.seed:
        seed = int(options.seed)
    else:
        seed = random.randint(0,65536)
    if len(args)>=1:
        world_name = args[0]
    else:
        world_name = "seed_%i" % seed
    if options.step:
        step = check_step(options.step)
    else:
        step = Step.get_by_name("full")
    width = 512
    height = 512

    print('Lands world generator')
    print('---------------------')
    print(' seed      : %i' % seed)
    print(' name      : %s' % world_name)
    print(' width     : %i' % width)
    print(' height    : %i' % height)
    print(' operation : %s generation' % operation)
    print(' step      : %s' % step.name)

    print('') # empty line
    print('starting...')
    if operation=='world':
        generate_world(seed, world_name, options.output_dir, width, height, step)
    elif operation=='plates':
        generate_plates(seed, world_name, options.output_dir)
    else:
        raise Exception('Unknown operation: valid operations are %s' % OPERATIONS)
    print('...done')

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