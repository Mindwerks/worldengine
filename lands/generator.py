__author__ = 'Federico Tomassetti'

from optparse import OptionParser
import os
from lands.plates import world_gen
from lands.draw import *
from lands.world import *
from PIL import Image

with open("lands/version.py") as f:
    code = compile(f.read(), "lands/version.py", 'exec')
    exec(code)

if sys.version_info > (2,):
    xrange = range

VERSION = __version__

OPERATIONS = 'world|plates|ancient_map'


def draw_oldmap(world, filename, resize_factor):
    img = Image.new('RGBA', (world.width*resize_factor, world.height*resize_factor))
    pixels = img.load()
    drawing_functions.draw_oldmap_on_pixels(world, pixels, resize_factor)
    img.save(filename)


def generate_world(seed, world_name, output_dir, width, height, step, num_plates=10, world_format='pickle'):
    w = world_gen(world_name, seed, True, width, height, step, num_plates=num_plates)

    print('')  # empty line
    print('Producing ouput:')

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
    elevation, plates = geo.generate_plates_simulation(seed, width, height, num_plates=num_plates)

    # Generate images
    filename = '%s/plates_%s.png' % (output_dir, world_name)
    draw_simple_elevation(elevation, filename)
    print("+ plates image generated in '%s'" % filename)
    plates = geo.center_elevation_map(elevation, width, height)
    filename = '%s/centered_plates_%s.png' % (output_dir, world_name)
    draw_simple_elevation(elevation, filename)
    print("+ centered plates image generated in '%s'" % filename)


class Step(object):
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
    parser.add_option('-o', '--output', dest='output_dir',
                      help="generate files in OUTPUT", metavar="FILE", default='.')
    parser.add_option('-n', '--worldname', dest='world_name',
                      help="set WORLDNAME", metavar="WORLDNAME")
    parser.add_option('-b', '--protocol-buffer', dest='protobuf', action="store_true",
                      help="save using protocol buffer", default=False)
    parser.add_option('-s', '--seed', dest='seed',
                      help="use SEED to initialize the pseudo-random generation",
                      metavar="SEED")
    parser.add_option('-t', '--step', dest='step',
                      help="use STEP to specify how far to proceed in the world generation process", metavar="STEP")
    parser.add_option('-x', '--width', dest='width',
                      help="WIDTH of the world to be generated", metavar="WIDTH",
                      default='512')
    parser.add_option('-y', '--height', dest='height',
                      help="HEIGHT of the world to be generated", metavar="HEIGHT",
                      default='512')
    parser.add_option('-w', '--worldfile', dest='world_file',
                      help="WORLD_FILE to be loaded (for ancient_map operation)", metavar="WORLD_FILE")
    parser.add_option('-g', '--generatedfile', dest='generated_file',
                      help="name of the GENERATED_FILE (for ancient_map operation)", metavar="GENERATED_FILE")
    parser.add_option('-f', '--resize-factor', dest='resize_factor',
                      help="resize factor", metavar="RESIZE_FACTOR", default='1')
    parser.add_option('-p', '--plates-resolution', dest='plates_resolution',
                      help="plates resolution", metavar="PLATES_RESOLUTION", default='512')
    parser.add_option('-q', '--number-of-plates', dest='number_of_plates',
                      help="number of plates", metavar="NUMBER_OF_PLATES", default='10')
    parser.add_option('-r', '--rivers', dest='rivers_map',
                      help="generate rivers map in RIVERSMAP_FILE", metavar="RIVERSMAP_FILE")
    parser.add_option('--gs', '--grayscale-heightmap', dest='grayscale_heightmap',
                      help='produce a grayscale heightmap in GRAYSCALE_FILE', metavar="GRAYSCALE_FILE")

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

    world_format = 'pickle'
    if options.protobuf:
        world_format = 'protobuf'

    generation_operation = (operation == 'world') or (operation == 'plates')

    resize_factor = int(options.resize_factor)

    produce_grayscale_heightmap = options.grayscale_heightmap
    if produce_grayscale_heightmap and not generation_operation:
        usage(error="Grayscale heightmap can be produced only during world generation")

    produce_rivers_map = options.rivers_map
    if produce_rivers_map and not generation_operation:
        usage(error="Rivers map can be produced only during world generation")

    print('Lands - a world generator (v. %s)' % VERSION)
    print('-----------------------')
    if generation_operation:
        print(' seed              : %i' % seed)
        print(' name              : %s' % world_name)
        print(' width             : %i' % width)
        print(' height            : %i' % height)
        print(' plates resolution : %i' % plates_resolution)
        print(' number of plates  : %i' % number_of_plates)
        print(' world format      : %s' % world_format)
    print(' operation         : %s generation' % operation)
    if generation_operation:
        print(' step              : %s' % step.name)
    if operation=='ancient_map':
        print(' resize factor     : %i' % resize_factor)
    if produce_grayscale_heightmap:
        print(' + greyscale heightmap in "%s"' % produce_grayscale_heightmap)
    if produce_rivers_map:
        print(' + rivers map in "%s"' % produce_rivers_map)

    print('')  # empty line
    print('starting (it could take a few minutes) ...')
    if operation == 'world':
        world = generate_world(seed, world_name, options.output_dir, width, height, step, num_plates=number_of_plates,
                               world_format=world_format)
        if produce_grayscale_heightmap:
            generate_grayscale_heightmap(world, produce_grayscale_heightmap)
        if produce_rivers_map:
            generate_rivers_map(world, produce_rivers_map)

    elif operation == 'plates':
        generate_plates(seed, world_name, options.output_dir, width, height, num_plates=number_of_plates)
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
