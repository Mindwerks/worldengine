__author__ = 'Federico Tomassetti'

import sys
from PIL import Image
from optparse import OptionParser, OptionGroup
import os

import lands.geo
from lands.plates import world_gen
from lands.draw import *
from lands.drawing_functions import *
from lands.world import *
from lands.common import *
from lands.step import Step
from lands.version import __version__

if sys.version_info > (2,):
    xrange = range

VERSION = __version__

OPERATIONS = 'world|plates|ancient_map'
SEA_COLORS = 'blue|brown'
STEPS      = 'plates|precipitations|full'


def draw_oldmap(world, filename, resize_factor, sea_color, verbose=True):
    img = Image.new('RGBA', (world.width*resize_factor, world.height*resize_factor))
    pixels = img.load()
    draw_oldmap_on_pixels(world, pixels, resize_factor, sea_color, verbose)
    img.save(filename)


def generate_world(world_name, width, height, seed, num_plates, output_dir,
        step, ocean_level, world_format='pickle', verbose=True):

    w = world_gen(world_name, width, height, seed, num_plates, ocean_level, step, verbose=verbose )

    print('')  # empty line
    print('Producing ouput:')
    sys.stdout.flush()

    # Save data
    filename = "%s/%s.world" % (output_dir, world_name)
    with open(filename, "wb") as f:
        if world_format == 'pickle':
            pickle.dump(w, f, pickle.HIGHEST_PROTOCOL)
        elif world_format == 'protobuf':
            f.write(w.protobuf_serialize())
        else:
            print("Unknown format '%s', not saving " % world_format)
    print("* world data saved in '%s'" % filename)
    sys.stdout.flush()

    # Generate images
    filename = '%s/%s_ocean.png' % (output_dir, world_name)
    draw_ocean(w.ocean, filename)
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
    draw_simple_elevation(e_as_array, filename, shadow=True, width=width, height=height)
    print("* elevation image generated in '%s'" % filename)
    return w


def generate_grayscale_heightmap(world, filename):
    draw_grayscale_heightmap(world, filename)
    print("+ grayscale heightmap generated in '%s'" % filename)


def generate_rivers_map(world, filename):
    draw_riversmap(world, filename)
    print("+ rivers map generated in '%s'" % filename)


def generate_plates(seed, world_name, output_dir, width, height, num_plates=10):
    elevation, plates = generate_plates_simulation(seed, width, height, num_plates=num_plates)

    # Generate images
    filename = '%s/plates_%s.png' % (output_dir, world_name)
    draw_simple_elevation(elevation, filename)
    print("+ plates image generated in '%s'" % filename)
    plates = geo.center_elevation_map(elevation, width, height)
    filename = '%s/centered_plates_%s.png' % (output_dir, world_name)
    draw_simple_elevation(elevation, filename)
    print("+ centered plates image generated in '%s'" % filename)


def is_pow_of_two(num):
    return ((num & (num - 1)) == 0) and num != 0


def check_step(step_name):
    step = Step.get_by_name(step_name)
    if step == None:
        print("ERROR: unknown step name, using default 'full'")
        return Step.get_by_name("full")
    else:
        return step


def operation_ancient_map(world, map_filename, resize_factor, sea_color):
    draw_oldmap(world, map_filename, resize_factor, sea_color)
    print("+ ancient map generated in '%s'" % map_filename)


def main():

    parser = OptionParser(usage = "usage: %prog [options] ["+OPERATIONS+"]", version="%prog " +VERSION)
    parser.add_option('-o', '--output-dir', dest='output_dir',
                      help="generate files in DIR [default = '%default']", metavar="DIR", default='.')
    parser.add_option('-n', '--worldname', dest='world_name',
                      help="set world name to STR. output is stored in a world file with the name format 'STR.world'. If a name is not provided, then seed_N.world, where N=SEED", metavar="STR")
    parser.add_option('-b', '--protocol-buffer', dest='protobuf', action="store_true",
                      help="Save world file using protocol buffer format. Default = store using pickle format", default=False)   #TODO: add description of protocol buffer
    parser.add_option('-s', '--seed', dest='seed', type="int",
                      help="Use seed=N to initialize the pseudo-random generation. If not provided, one will be selected for you.",
                      metavar="N")
    parser.add_option('-t', '--step', dest='step',
                      help="Use step=["+STEPS+"] to specify how far to proceed in the world generation process. [default='%default']",
                      metavar="STR", default="full")
                      #TODO --step appears to be duplicate of OPERATIONS. Especially if ancient_map is added to --step
    parser.add_option('-x', '--width', dest='width', type="int",
                      help="N = width of the world to be generated [default=%default]", metavar="N",
                      default='512')
    parser.add_option('-y', '--height', dest='height', type="int",
                      help="N = height of the world to be generated [default=%default]", metavar="N",
                      default='512')
    parser.add_option('-q', '--number-of-plates', dest='number_of_plates', type="int",
                      help="N = number of plates [default = %default]", metavar="N", default='10')
    parser.add_option('--recursion_limit', dest='recursion_limit', type="int",
                      help="Set the recursion limit [default = %default]", metavar="N", default='2000')
    parser.add_option('-v', '--verbose', dest='verbose', action="store_true",
                      help="Enable verbose messages", default=False)

    #-----------------------------------------------------
    g_generate = OptionGroup(parser, "Generate Options",
                    "These options are only useful in plate and world modes")
    g_generate.add_option('-r', '--rivers', dest='rivers_map',
                      help="generate rivers map in FILE", metavar="FILE")
    g_generate.add_option('--gs', '--grayscale-heightmap', dest='grayscale_heightmap',
                      help='produce a grayscale heightmap in FILE', metavar="FILE")
    g_generate.add_option('--ocean_level', dest='ocean_level', type="float",
                      help='elevation cut off for sea level [default = %default]', metavar="N", default=1.0)
    parser.add_option_group(g_generate)

    #-----------------------------------------------------
    g_ancient_map = OptionGroup(parser, "Ancient Map Options",
                    "These options are only useful in ancient_map mode")
    g_ancient_map.add_option('-w', '--worldfile', dest='world_file',
                      help="FILE to be loaded", metavar="FILE")
    g_ancient_map.add_option('-g', '--generatedfile', dest='generated_file',
                      help="name of the FILE", metavar="FILE")
    g_ancient_map.add_option('-f', '--resize-factor', dest='resize_factor', type="int",
                      help="resize factor (only integer values). Note this can only be used to increase the size of the map [default=%default]", metavar="N", default='1')
    g_ancient_map.add_option('--sea_color', dest='sea_color',
                      help="string for color ["+SEA_COLORS+"]", metavar="S", default="brown")
                      #TODO: allow for RGB specification as [r g b], ie [0.5 0.5 0.5] for gray
    parser.add_option_group(g_ancient_map)

    (options, args) = parser.parse_args()

    if not os.path.isdir(options.output_dir):
        raise Exception("Output dir does not exist or it is not a dir")

    # it needs to be increased to be able to generate very large maps
    # the limit is hit when drawing ancient maps
    sys.setrecursionlimit(options.recursion_limit)

    try:
        number_of_plates = int(options.number_of_plates)
        if number_of_plates < 1 or number_of_plates > 100:
            usage(error="Number of plates should be a in [1, 100]")
    except:
        usage(error="Number of plates should be a number")

    if len(args) > 1:
        parser.print_help()
        usage("Only 1 operation allowed ["+OPERATIONS+"]")
    if len(args) == 1:
        if args[0] in OPERATIONS:
            operation = args[0]
        else:
            usage("Unknown operation: %s" % args[0])
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

    step = check_step(options.step)

    world_format = 'pickle'
    if options.protobuf:
        world_format = 'protobuf'

    generation_operation = (operation == 'world') or (operation == 'plates')

    produce_grayscale_heightmap = options.grayscale_heightmap
    if produce_grayscale_heightmap and not generation_operation:
        usage(error="Grayscale heightmap can be produced only during world generation")

    if options.rivers_map and not generation_operation:
        usage(error="Rivers map can be produced only during world generation")

    print('Lands - a world generator (v. %s)' % VERSION)
    print('-----------------------')
    print(' operation         : %s generation' % operation)
    if generation_operation:
        print(' seed              : %i' % seed)
        print(' name              : %s' % world_name)
        print(' width             : %i' % options.width)
        print(' height            : %i' % options.height)
        print(' number of plates  : %i' % number_of_plates)
        print(' world format      : %s' % world_format)
        print(' step              : %s' % step.name)
        if produce_grayscale_heightmap:
            print(' + greyscale heightmap in "%s"' % produce_grayscale_heightmap)
        else:
            print(' (no greyscale heightmap)')
        if options.rivers_map:
            print(' + rivers map in "%s"' % options.rivers_map)
        else:
            print(' (no rivers map)')
    if operation=='ancient_map':
        print(' resize factor     : %i' % options.resize_factor)
        print(' world file        : %s' % options.world_file)
        print(' sea color         : %s' % options.sea_color)

    print('')  # empty line
    print('starting (it could take a few minutes) ...')

    set_verbose(options.verbose)


    if operation == 'world':
        world = generate_world(world_name, options.width, options.height,
                seed, number_of_plates, options.output_dir,
                step, options.ocean_level, world_format, options.verbose)
        if produce_grayscale_heightmap:
            generate_grayscale_heightmap(world, produce_grayscale_heightmap)
        if options.rivers_map:
            generate_rivers_map(world, options.rivers_map)

    elif operation == 'plates':
        generate_plates(seed, world_name, options.output_dir, options.width, options.height, num_plates=number_of_plates)

    elif operation == 'ancient_map':
        # First, some error checking
        if (options.sea_color == "blue"):
            sea_color = (142, 162, 179, 255)
        elif (options.sea_color == "brown"):
            sea_color = (212, 198, 169, 255)
        else:
            usage("Unknown sea color: " +args[0] +"  Select from [" +SEA_COLORS +"]")
        if not options.world_file:
            usage("For generating an ancient map is necessary to specify the world to be used (-w option)")
        world = World.from_pickle_file(options.world_file)

        if not options.generated_file:
            options.generated_file = "ancient_map_%s.png" % world.name
        operation_ancient_map(world, options.generated_file, options.resize_factor, sea_color)
    else:
        raise Exception('Unknown operation: valid operations are %s' % OPERATIONS)

    print('...done')


def usage(error=None):
    print(' -------------------------------------------------------------------------')
    print(' Federico Tomassetti, 2013-2015')
    print(' Lands - a world generator (v. %s)' % VERSION)
    print(' ')
    print(' generator <world_name> [operation] [options]')
    print(' possible operations: %s' % OPERATIONS)
    print(' use -h to see options')
    print(' -------------------------------------------------------------------------')
    if error:
        print("ERROR: %s" % error)
    sys.exit(' ')

# -------------------------------
if __name__ == "__main__":
    main()
