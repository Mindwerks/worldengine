__author__ = 'Federico Tomassetti'

import sys
from optparse import OptionParser

from plates import world_gen
from draw import draw_biome, draw_precipitation, draw_temperature_levels
import geo
import draw
import drawing_functions
import os
from world import *

from PIL import Image


OPERATIONS = 'world|plates|ancient_map'


def draw_oldmap(world, filename, resize_factor):
    img = Image.new('RGBA', (world.width*resize_factor, world.height*resize_factor))
    pixels = img.load()
    drawing_functions.draw_oldmap_on_pixels(world, pixels, resize_factor)
    img.save(filename)


def generate_world(seed, world_name, output_dir, width, height, step, num_plates=10, map_side=512):
    w = world_gen(world_name, seed, True, width, height, step, num_plates=num_plates, map_side=map_side)

    print('')  # empty line
    print('Producing ouput:')

    # Save data
    filename = "%s/%s.world" % (output_dir, world_name)
    with open(filename, "w") as f:
        pickle.dump(w, f, pickle.HIGHEST_PROTOCOL)
    print("* world data saved in '%s'" % filename)

    # Generate images
    filename = '%s/%s_ocean.png' % (output_dir, world_name)
    draw.draw_ocean(w.ocean, filename)
    print("* ocean image generated in '%s'" % filename)

    if step.include_precipitations:
        filename = '%s/%s_precipitation.png' % (output_dir, world_name)
        draw_precipitation(w, filename)
        print("* precipitation image generated in '%s'" % filename)
        filename = '%s/%s_temperature.png' % (output_dir, world_name)
        draw_temperature_levels(w, filename)
        print("* temperature image generated in '%s'" % filename)

    if step.include_biome:
        filename = '%s/%s_biome.png' % (output_dir, world_name)
        draw_biome(w.biome, filename)
        print("* biome image generated in '%s'" % filename)

    filename = '%s/%s_elevation.png' % (output_dir, world_name)
    e_as_array = []
    for y in xrange(height):
        for x in xrange(width):
            e_as_array.append(w.elevation['data'][y][x])
    draw.draw_simple_elevation(e_as_array, filename, shadow=True, width=width, height=height)
    print("* elevation image generated in '%s'" % filename)


def generate_plates(seed, world_name, output_dir, width, height, num_plates=10, map_side=512):
    plates = geo.generate_plates_simulation(seed, width, height, num_plates=num_plates, map_side=map_side)

    # Generate images
    filename = '%s/plates_%s.png' % (output_dir, world_name)
    draw.draw_simple_elevation(plates, filename)
    print("+ plates image generated in '%s'" % filename)
    plates = geo.center_elevation_map(plates, width, height)
    filename = '%s/centered_plates_%s.png' % (output_dir, world_name)
    draw.draw_simple_elevation(plates, filename)
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
        if name == "plates":
            step = Step(name)
        elif name == "precipitations":
            step = Step(name)
            step.include_precipitations = True
        elif name == "full":
            step = Step(name)
            step.include_precipitations = True
            step.include_erosion = True
            step.include_biome = True

        return step

def is_pow_of_two(num):
    return ((num & (num - 1)) == 0) and num != 0

def check_step(step_name):
    step = Step.get_by_name(step_name)
    if step == None:
        print("ERROR: unknown step name, using default 'full'")
        return Step.get_by_name("full")
    else:
        return step

def operation_ancient_map(world, map_filename, resize_factor):
    draw_oldmap(world, map_filename, resize_factor)
    print("+ ancient map generated in '%s'" % map_filename)


def main():
    # it needs to be increased to be able to generate very large maps
    # the limit is hit when drawing ancient maps
    sys.setrecursionlimit(2000)

    parser = OptionParser()
    parser.add_option('-o', '--output', dest='output_dir', help="generate files in OUTPUT", metavar="FILE", default='.')
    parser.add_option('-n', '--worldname', dest='world_name', help="set WORLDNAME", metavar="WORLDNAME")
    parser.add_option('-s', '--seed', dest='seed', help="use SEED to initialize the pseudo-random generation",
                      metavar="SEED")
    parser.add_option('-t', '--step', dest='step',
                      help="use STEP to specify how far to proceed in the world generation process", metavar="STEP")
    parser.add_option('-x', '--width', dest='width', help="WIDTH of the world to be generated", metavar="WIDTH",
                      default='512')
    parser.add_option('-y', '--height', dest='height', help="HEIGHT of the world to be generated", metavar="HEIGHT",
                      default='512')
    parser.add_option('-w', '--worldfile', dest='world_file', help="WORLD_FILE to be loaded (for ancient_map operation)", metavar="WORLD_FILE")
    parser.add_option('-g', '--generatedfile', dest='generated_file', help="name of the GENERATED_FILE (for ancient_map operation)", metavar="GENERATED_FILE")
    parser.add_option('-f', '--resize-factor', dest='resize_factor', help="resize factor", metavar="RESIZE_FACTOR", default='1')
    parser.add_option('-p', '--plates-resolution', dest='plates_resolution', help="plates resolution", metavar="PLATES_RESOLUTION", default='512')
    parser.add_option('-q', '--number-of-plates', dest='number_of_plates', help="number of plates", metavar="NUMBER_OF_PLATES", default='10')

    (options, args) = parser.parse_args()

    if not os.path.isdir(options.output_dir):
        raise Exception("Output dir does not exist or it is not a dir")

    try:
        plates_resolution = int(options.plates_resolution)
        if plates_resolution < 128 or plates_resolution > 65536:
            usage(error="Plates resolution should be a power of 2 in [128, 65536]")
        if not is_pow_of_two(plates_resolution):
            usage(error="Plates resolution should be a power of 2 in [128, 65536]")
    except:
        usage(error="Plates resolution should be a number")

    try:
        number_of_plates = int(options.number_of_plates)
        if number_of_plates < 1 or number_of_plates > 100:
            usage(error="Number of plates should be a in [1, 100]")
    except:
        usage(error="Number of plates should be a number")

    try:
        width = int(options.width)
    except:
        usage(error="Width should be a number")

    try:
        height = int(options.height)
    except:
        usage(error="Height should be a number")

    if len(args) > 1:
        usage()
    if len(args) == 1:
        if args[0] in OPERATIONS:
            operation = args[0]
        else:
            usage("Unknown operation")
    else:
        operation = 'world'
    random.seed()
    if options.seed:
        seed = int(options.seed)
    else:
        seed = random.randint(0, 65536)
    if options.world_name:
        world_name = options.world_name
    else:
        world_name = "seed_%i" % seed
    if options.step:
        step = check_step(options.step)
    else:
        step = Step.get_by_name("full")

    generation_operation = (operation == 'world') or (operation == 'plates')

    resize_factor = int(options.resize_factor)

    print('Lands - world generator')
    print('-----------------------')
    if generation_operation:
        print(' seed              : %i' % seed)
        print(' name              : %s' % world_name)
        print(' width             : %i' % width)
        print(' height            : %i' % height)
        print(' plates resolution : %i' % plates_resolution)
        print(' number of plates  : %i' % number_of_plates)
    print(' operation         : %s generation' % operation)
    if generation_operation:
        print(' step              : %s' % step.name)
    if operation=='ancient_map':
        print(' resize factor     : %i' % resize_factor)

    print('')  # empty line
    print('starting (it could take a few minutes) ...')
    if operation == 'world':
        generate_world(seed, world_name, options.output_dir, width, height, step, num_plates=number_of_plates, map_side=plates_resolution)
    elif operation == 'plates':
        generate_plates(seed, world_name, options.output_dir, width, height, num_plates=number_of_plates, map_side=plates_resolution)
    elif operation == 'ancient_map':
        if not options.world_file:
            usage("For generating an ancient map is necessary to specify the world to be used (-w option)")
        world = World.from_pickle_file(options.world_file)
        if options.generated_file:
            map_filename = options.generated_file
        else:
            map_filename = "ancient_map_%s.png" % world.name
        operation_ancient_map(world, map_filename, resize_factor)
    else:
        raise Exception('Unknown operation: valid operations are %s' % OPERATIONS)
    print('...done')


def usage(error=None):
    print ' -------------------------------------------------------------------------'
    print ' Federico Tomassetti, 2013-2014'
    print ' World generator'
    print ' '
    print ' generator <world_name> [operation] [options]'
    print ' possible operations: %s' % OPERATIONS
    print ' use -h to see options'
    print ' -------------------------------------------------------------------------'
    if error:
        print("ERROR: %s" % error)
    sys.exit(' ')

# -------------------------------
if __name__ == "__main__":
    main()
