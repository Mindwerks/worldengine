import sys
from argparse import ArgumentParser
import os
import numpy
import pickle
import worldengine.generation as geo
from worldengine.common import array_to_matrix, set_verbose, print_verbose
from worldengine.draw import draw_ancientmap_on_file, draw_biome_on_file, draw_ocean_on_file, \
    draw_precipitation_on_file, draw_grayscale_heightmap_on_file, draw_simple_elevation_on_file, \
    draw_temperature_levels_on_file, draw_riversmap_on_file, draw_scatter_plot_on_file, draw_satellite_on_file
from worldengine.plates import world_gen, generate_plates_simulation
from worldengine.imex import export
from worldengine.step import Step
from worldengine.world import World
from worldengine.version import __version__

VERSION = __version__

OPERATIONS = 'world|plates|ancient_map|info|export'
SEA_COLORS = 'blue|brown'
STEPS = 'plates|precipitations|full'


def generate_world(world_name, width, height, seed, num_plates, output_dir,
                   step, ocean_level, temps, humids, world_format='protobuf',
                   gamma_curve=1.25, curve_offset=.2, fade_borders=True,
                   verbose=True, black_and_white=False):
    w = world_gen(world_name, width, height, seed, temps, humids, num_plates, ocean_level,
                  step, gamma_curve=gamma_curve, curve_offset=curve_offset,
                  fade_borders=fade_borders, verbose=verbose)

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
    draw_ocean_on_file(w.ocean, filename)
    print("* ocean image generated in '%s'" % filename)

    if step.include_precipitations:
        filename = '%s/%s_precipitation.png' % (output_dir, world_name)
        draw_precipitation_on_file(w, filename, black_and_white)
        print("* precipitation image generated in '%s'" % filename)
        filename = '%s/%s_temperature.png' % (output_dir, world_name)
        draw_temperature_levels_on_file(w, filename, black_and_white)
        print("* temperature image generated in '%s'" % filename)

    if step.include_biome:
        filename = '%s/%s_biome.png' % (output_dir, world_name)
        draw_biome_on_file(w, filename)
        print("* biome image generated in '%s'" % filename)

    filename = '%s/%s_elevation.png' % (output_dir, world_name)
    sea_level = w.sea_level()
    draw_simple_elevation_on_file(w, filename, sea_level=sea_level)
    print("* elevation image generated in '%s'" % filename)
    return w


def generate_grayscale_heightmap(world, filename):
    draw_grayscale_heightmap_on_file(world, filename)
    print("+ grayscale heightmap generated in '%s'" % filename)


def generate_rivers_map(world, filename):
    draw_riversmap_on_file(world, filename)
    print("+ rivers map generated in '%s'" % filename)

def draw_scatter_plot(world, filename):
    draw_scatter_plot_on_file(world, filename)
    print("+ scatter plot generated in '%s'" % filename)

def draw_satellite_map(world, filename):
    draw_satellite_on_file(world, filename)
    print("+ satellite map generated in '%s'" % filename)

def generate_plates(seed, world_name, output_dir, width, height,
                    num_plates=10):
    """
    Eventually this method should be invoked when generation is called at
    asked to stop at step "plates", it should not be a different operation
    :param seed:
    :param world_name:
    :param output_dir:
    :param width:
    :param height:
    :param num_plates:
    :return:
    """
    elevation, plates = generate_plates_simulation(seed, width, height,
                                                   num_plates=num_plates)

    world = World(world_name, width, height, seed, num_plates, -1.0, "plates")
    world.set_elevation(numpy.array(elevation).reshape(height, width), None)
    world.set_plates(array_to_matrix(plates, width, height))

    # Generate images
    filename = '%s/plates_%s.png' % (output_dir, world_name)
    draw_simple_elevation_on_file(world, filename, None)
    print("+ plates image generated in '%s'" % filename)
    geo.center_land(world)
    filename = '%s/centered_plates_%s.png' % (output_dir, world_name)
    draw_simple_elevation_on_file(world, filename, None)
    print("+ centered plates image generated in '%s'" % filename)


def check_step(step_name):
    step = Step.get_by_name(step_name)
    if step is None:
        print("ERROR: unknown step name, using default 'full'")
        return Step.get_by_name("full")
    else:
        return step


def operation_ancient_map(world, map_filename, resize_factor, sea_color,
                          draw_biome, draw_rivers, draw_mountains,
                          draw_outer_land_border):
    draw_ancientmap_on_file(world, map_filename, resize_factor, sea_color,
                            draw_biome, draw_rivers, draw_mountains,
                            draw_outer_land_border)
    print("+ ancient map generated in '%s'" % map_filename)


def __get_last_byte__(filename):
    with open(filename, 'rb') as input_file:
        data = tmp_data = input_file.read(1024 * 1024)
        while tmp_data:
            tmp_data = input_file.read(1024 * 1024)
            if tmp_data:
                data = tmp_data
    return data[len(data) - 1]


def __varint_to_value__(varint):
    # See https://developers.google.com/protocol-buffers/docs/encoding for details

    # to convert it to value we must start from the first byte
    # and add to it the second last multiplied by 128, the one after
    # multiplied by 128 ** 2 and so on
    if len(varint) == 1:
        return varint[0]
    else:
        return varint[0] + 128 * __varint_to_value__(varint[1:])


def __get_tag__(filename):
    with open(filename, 'rb') as ifile:
        # drop first byte, it should tell us the protobuf version and it
        # should be normally equal to 8
        data = ifile.read(1)
        if not data:
            return None
        done = False
        tag_bytes = []
        # We read bytes until we find a bit with the MSB not set
        while data and not done:
            data = ifile.read(1)
            if not data:
                return None
            value = ord(data)
            tag_bytes.append(value % 128)
            if value < 128:
                done = True
        # to convert it to value we must start from the last byte
        # and add to it the second last multiplied by 128, the one before
        # multiplied by 128 ** 2 and so on
        return __varint_to_value__(tag_bytes)


def __seems_protobuf_worldfile__(world_filename):
    worldengine_tag = __get_tag__(world_filename)
    return worldengine_tag == World.worldengine_tag()


def __seems_pickle_file__(world_filename):
    last_byte = __get_last_byte__(world_filename)
    return str(last_byte) == '.'


def load_world(world_filename):
    pb = __seems_protobuf_worldfile__(world_filename)
    pi = __seems_pickle_file__(world_filename)
    if pb and pi:
        print("we cannot distinguish if the file is a pickle or a protobuf "
              "world file. Trying to load first as protobuf then as pickle "
              "file")
        try:
            return World.open_protobuf(world_filename)
        except Exception:
            try:
                return World.from_pickle_file(world_filename)
            except Exception:
                raise Exception("Unable to load the worldfile neither as protobuf or pickle file")

    elif pb:
        return World.open_protobuf(world_filename)
    elif pi:
        return World.from_pickle_file(world_filename)
    else:
        raise Exception("The given worldfile does not seem a pickle or a protobuf file")


def print_world_info(world):
    print(" name               : %s" % world.name)
    print(" width              : %i" % world.width)
    print(" height             : %i" % world.height)
    print(" seed               : %i" % world.seed)
    print(" no plates          : %i" % world.n_plates)
    print(" ocean level        : %f" % world.ocean_level)
    print(" step               : %s" % world.step.name)

    print(" has biome          : %s" % world.has_biome())
    print(" has humidity       : %s" % world.has_humidity())
    print(" has irrigation     : %s" % world.has_irrigation())
    print(" has permeability   : %s" % world.has_permeability())
    print(" has watermap       : %s" % world.has_watermap())
    print(" has precipitations : %s" % world.has_precipitations())
    print(" has temperature    : %s" % world.has_temperature())


def main():
    parser = ArgumentParser(
        usage="usage: %(prog)s [options] [" + OPERATIONS + "]")
    parser.add_argument('OPERATOR', nargs='?')
    parser.add_argument('FILE', nargs='?')
    parser.add_argument(
        '-o', '--output-dir', dest='output_dir',
        help="generate files in DIR [default = '%(default)s']",
        metavar="DIR", default='.')
    parser.add_argument(
        '-n', '--worldname', dest='world_name',
        help="set world name to STR. output is stored in a " +
             "world file with the name format 'STR.world'. If " +
             "a name is not provided, then seed_N.world, " +
             "where N=SEED",
        metavar="STR")
    parser.add_argument('-s', '--seed', dest='seed', type=int,
                        help="Use seed=N to initialize the pseudo-random " +
                             "generation. If not provided, one will be " +
                             "selected for you.",
                        metavar="N")
    parser.add_argument('-t', '--step', dest='step',
                        help="Use step=[" + STEPS + "] to specify how far " +
                             "to proceed in the world generation process. " +
                             "[default='%(default)s']",
                        metavar="STR", default="full")
    # TODO --step appears to be duplicate of OPERATIONS. Especially if
    # ancient_map is added to --step
    parser.add_argument('-x', '--width', dest='width', type=int,
                        help="N = width of the world to be generated " +
                             "[default=%(default)s]",
                        metavar="N",
                        default='512')
    parser.add_argument('-y', '--height', dest='height', type=int,
                        help="N = height of the world to be generated " +
                             "[default=%(default)s]",
                        metavar="N",
                        default='512')
    parser.add_argument('-q', '--number-of-plates', dest='number_of_plates',
                        type=int,
                        help="N = number of plates [default = %(default)s]",
                        metavar="N", default='10')
    parser.add_argument('--recursion_limit', dest='recursion_limit', type=int,
                        help="Set the recursion limit [default = %(default)s]",
                        metavar="N", default='2000')
    parser.add_argument('-v', '--verbose', dest='verbose', action="store_true",
                        help="Enable verbose messages", default=False)
    parser.add_argument('--version', dest='version', action="store_true",
                        help="Display version information", default=False)
    parser.add_argument('--bw', '--black-and-white', dest='black_and_white',
                        action="store_true",
                        help="generate maps in black and white",
                        default=False)

    # -----------------------------------------------------
    g_generate = parser.add_argument_group(
        "Generate Options", "These options are only useful in plate and " +
        "world modes")
    g_generate.add_argument('-r', '--rivers', dest='rivers_map',
                            action="store_true", help="generate rivers map")
    g_generate.add_argument('--gs', '--grayscale-heightmap',
                            dest='grayscale_heightmap', action="store_true",
                            help='produce a grayscale heightmap')
    g_generate.add_argument('--ocean_level', dest='ocean_level', type=float,
                            help='elevation cut off for sea level " +'
                                 '[default = %(default)s]',
                            metavar="N", default=1.0)
    g_generate.add_argument('--temps', dest='temps', 
                        help="Provide alternate ranges for temperatures. " +
                             "If not provided, the default values will be used. \n" +
                             "[default = .126/.235/.406/.561/.634/.876]",
                            metavar="#/#/#/#/#/#")
    g_generate.add_argument('--humidity', dest='humids', 
                        help="Provide alternate ranges for humidities. " +
                             "If not provided, the default values will be used. \n" +
                            "[default = .059/.222/.493/.764/.927/.986/.998]",
                            metavar="#/#/#/#/#/#/#")
    g_generate.add_argument('-gv', '--gamma-value', dest='gv', type=float,
                        help="N = Gamma value for temperature/precipitation " +
                             "gamma correction curve. [default = %(default)s]",
                        metavar="N", default='1.25')
    g_generate.add_argument('-go', '--gamma-offset', dest='go', type=float,
                        help="N = Adjustment value for temperature/precipitation " +
                             "gamma correction curve. [default = %(default)s]",
                        metavar="N", default='.2')
    g_generate.add_argument('--not-fade-borders', dest='fade_borders', action="store_false",
                               help="Not fade borders",
                               default=True)
    g_generate.add_argument('--scatter', dest='scatter_plot',
                            action="store_true", help="generate scatter plot")

    g_generate.add_argument('--sat', dest='satelite_map',
                            action="store_true", help="generate satellite map")

    # -----------------------------------------------------
    g_ancient_map = parser.add_argument_group(
        "Ancient Map Options", "These options are only useful in " +
        "ancient_map mode")
    g_ancient_map.add_argument('-w', '--worldfile', dest='world_file',
                               help="FILE to be loaded", metavar="FILE")
    g_ancient_map.add_argument('-g', '--generatedfile', dest='generated_file',
                               help="name of the FILE", metavar="FILE")
    g_ancient_map.add_argument(
        '-f', '--resize-factor', dest='resize_factor', type=int,
        help="resize factor (only integer values). " +
             "Note this can only be used to increase " +
             "the size of the map [default=%(default)s]",
        metavar="N", default='1')
    g_ancient_map.add_argument('--sea_color', dest='sea_color',
                               help="string for color [" + SEA_COLORS + "]",
                               metavar="S", default="brown")

    g_ancient_map.add_argument('--not-draw-biome', dest='draw_biome',
                               action="store_false",
                               help="Not draw biome",
                               default=True)
    g_ancient_map.add_argument('--not-draw-mountains', dest='draw_mountains',
                               action="store_false",
                               help="Not draw mountains",
                               default=True)
    g_ancient_map.add_argument('--not-draw-rivers', dest='draw_rivers',
                               action="store_false",
                               help="Not draw rivers",
                               default=True)
    g_ancient_map.add_argument('--draw-outer-border', dest='draw_outer_border',
                               action="store_true",
                               help="Draw outer land border",
                               default=False)
    # TODO: allow for RGB specification as [r g b], ie [0.5 0.5 0.5] for gray

    # -----------------------------------------------------
    export_options = parser.add_argument_group(
        "Export Options", "You can specify the formats you wish the generated output to be in. ")
    export_options.add_argument("--export-format", dest="export_format", type=str,
                                help="Export to a specific format such as BMP or PNG. " +
                                "See http://www.gdal.org/formats_list.html for possible formats.",
                                default="PNG")
    export_options.add_argument("--export-datatype", dest="export_datatype", type=str,
                                help="Type of stored data, e.g. uint16, int32, float32 etc.",
                                default="uint16")

    args = parser.parse_args()

    if args.version:
        usage()

    if os.path.exists(args.output_dir):
        if not os.path.isdir(args.output_dir):
            raise Exception("Output dir exists but it is not a dir")
    else:
        print('Directory does not exist, we are creating it')
        os.makedirs(args.output_dir)

    # it needs to be increased to be able to generate very large maps
    # the limit is hit when drawing ancient maps
    sys.setrecursionlimit(args.recursion_limit)

    if args.number_of_plates < 1 or args.number_of_plates > 100:
        usage(error="Number of plates should be in [1, 100]")

    operation = "world"
    if args.OPERATOR is None:
        pass
    elif args.OPERATOR is not None and args.OPERATOR.lower() not in OPERATIONS:
        parser.print_help()
        usage("Only 1 operation allowed [" + OPERATIONS + "]")
    else:
        operation = args.OPERATOR.lower()

    if args.OPERATOR == 'info' or args.OPERATOR == 'export':
        if args.FILE is None:
            parser.print_help()
            usage("For operation info only the filename should be specified")
        if not os.path.exists(args.FILE):
            usage("The specified world file does not exist")

    maxseed = numpy.iinfo(numpy.uint16).max  # there is a hard limit somewhere so seeds outside the uint16 range are considered unsafe
    if args.seed is not None:
        seed = int(args.seed)
        assert 0 <= seed <= maxseed, "Seed has to be in the range between 0 and %s, borders included." % maxseed
    else:
        seed = numpy.random.randint(0, maxseed)  # first-time RNG initialization is done automatically
    numpy.random.seed(seed)

    if args.world_name:
        world_name = args.world_name
    else:
        world_name = "seed_%i" % seed

    step = check_step(args.step)

    world_format = 'protobuf'

    generation_operation = (operation == 'world') or (operation == 'plates')

    if args.grayscale_heightmap and not generation_operation:
        usage(
            error="Grayscale heightmap can be produced only during world " +
                  "generation")

    if args.rivers_map and not generation_operation:
        usage(error="Rivers map can be produced only during world generation")

    if args.temps and not generation_operation:
        usage(error="temps can be assigned only during world generation")

    if args.temps and len(args.temps.split('/')) is not 6:
        usage(error="temps must have exactly 6 values")

    if args.go >= 1 or args.go < 0:
        usage(error="Gamma offset must be greater than or equal to 0 and less than 1")

    if args.gv <= 0:
        usage(error="Gamma value must be greater than 0")

    temps = [.874, .765, .594, .439, .366, .124]
    if args.temps:
        temps = args.temps.split('/')
        for x in range(0,len(temps)):
            temps[x] = 1 - float(temps[x])

    if args.humids and not generation_operation:
        usage(error="humidity can be assigned only during world generation")

    if args.humids and len(args.humids.split('/')) is not 7:
        usage(error="humidity must have exactly 7 values")

    humids = [.941, .778, .507, .236, 0.073, .014, .002]
    if args.humids:
        humids = args.humids.split('/')
        for x in range(0,len(humids)):
            humids[x] = 1 - float(humids[x])
    if args.scatter_plot and not generation_operation:
        usage(error="Scatter plot can be produced only during world generation")

    print('Worldengine - a world generator (v. %s)' % VERSION)
    print('-----------------------')
    if generation_operation:
        print(' operation            : %s generation' % operation)
        print(' seed                 : %i' % seed)
        print(' name                 : %s' % world_name)
        print(' width                : %i' % args.width)
        print(' height               : %i' % args.height)
        print(' number of plates     : %i' % args.number_of_plates)
        print(' world format         : %s' % world_format)
        print(' black and white maps : %s' % args.black_and_white)
        print(' step                 : %s' % step.name)
        print(' greyscale heightmap  : %s' % args.grayscale_heightmap)
        print(' rivers map           : %s' % args.rivers_map)
        print(' scatter plot         : %s' % args.scatter_plot)
        print(' satellite map        : %s' % args.satelite_map)
        print(' fade borders         : %s' % args.fade_borders)
        if args.temps:
            print(' temperature ranges   : %s' % args.temps)
        if args.humids:
            print(' humidity ranges      : %s' % args.humids)
        print(' gamma value          : %s' % args.gv)
        print(' gamma offset         : %s' % args.go)
    if operation == 'ancient_map':
        print(' operation              : %s generation' % operation)
        print(' resize factor          : %i' % args.resize_factor)
        print(' world file             : %s' % args.world_file)
        print(' sea color              : %s' % args.sea_color)
        print(' draw biome             : %s' % args.draw_biome)
        print(' draw rivers            : %s' % args.draw_rivers)
        print(' draw mountains         : %s' % args.draw_mountains)
        print(' draw land outer border : %s' % args.draw_outer_border)
        
    #Warning messages
    warnings = []
    if temps != sorted(temps, reverse=True):
        warnings.append("WARNING: Temperature array not in ascending order")
    if numpy.amin(temps) < 0:
        warnings.append("WARNING: Maximum value in temperature array greater than 1")
    if numpy.amax(temps) > 1:
        warnings.append("WARNING: Minimum value in temperature array less than 0")
    if humids != sorted(humids, reverse=True):
        warnings.append("WARNING: Humidity array not in ascending order")
    if numpy.amin(humids) < 0:
        warnings.append("WARNING: Maximum value in humidity array greater than 1")
    if numpy.amax(humids) > 1:
        warnings.append("WARNING: Minimum value in temperature array less than 0")

    if warnings:
        print("\n")
        for x in range(len(warnings)):
            print(warnings[x])

    set_verbose(args.verbose)

    if operation == 'world':
        print('')  # empty line
        print('starting (it could take a few minutes) ...')

        world = generate_world(world_name, args.width, args.height,
                               seed, args.number_of_plates, args.output_dir,
                               step, args.ocean_level, temps, humids, world_format,
                               gamma_curve=args.gv,curve_offset=args.go,
                               fade_borders=args.fade_borders,
                               verbose=args.verbose, black_and_white=args.black_and_white)
        if args.grayscale_heightmap:
            generate_grayscale_heightmap(world,
            '%s/%s_grayscale.png' % (args.output_dir, world_name))
        if args.rivers_map:
            generate_rivers_map(world,
            '%s/%s_rivers.png' % (args.output_dir, world_name))
        if args.scatter_plot:
            draw_scatter_plot(world,
            '%s/%s_scatter.png' % (args.output_dir, world_name))    
        if args.satelite_map:
            draw_satellite_map(world,
            '%s/%s_satellite.png' % (args.output_dir, world_name))    

    elif operation == 'plates':
        print('')  # empty line
        print('starting (it could take a few minutes) ...')

        generate_plates(seed, world_name, args.output_dir, args.width,
                        args.height, num_plates=args.number_of_plates)

    elif operation == 'ancient_map':
        print('')  # empty line
        print('starting (it could take a few minutes) ...')
        # First, some error checking
        if args.sea_color == "blue":
            sea_color = (142, 162, 179, 255)
        elif args.sea_color == "brown":
            sea_color = (212, 198, 169, 255)
        else:
            usage("Unknown sea color: " + args.sea_color +
                  " Select from [" + SEA_COLORS + "]")
        if not args.world_file:
            usage(
                "For generating an ancient map is necessary to specify the " +
                "world to be used (-w option)")
        world = load_world(args.world_file)

        print_verbose(" * world loaded")

        if not args.generated_file:
            args.generated_file = "ancient_map_%s.png" % world.name
        operation_ancient_map(world, args.generated_file,
                              args.resize_factor, sea_color,
                              args.draw_biome, args.draw_rivers,
                              args.draw_mountains, args.draw_outer_border)
    elif operation == 'info':
        world = load_world(args.FILE)
        print_world_info(world)
    elif operation == 'export':
        world = load_world(args.FILE)
        print_world_info(world)
        export(world, args.export_format, args.export_datatype,
               path = '%s/%s_elevation' % (args.output_dir, world_name))
    else:
        raise Exception(
            'Unknown operation: valid operations are %s' % OPERATIONS)

    print('...done')


def usage(error=None):
    print(
        ' -------------------------------------------------------------------')
    print(' Federico Tomassetti and Bret Curtis, 2011-2015')
    print(' Worldengine - a world generator (v. %s)' % VERSION)
    print(' ')
    print(' worldengine <world_name> [operation] [options]')
    print(' possible operations: %s' % OPERATIONS)
    print(' use -h to see options')
    print(
        ' -------------------------------------------------------------------')
    if error:
        print("ERROR: %s" % error)
    sys.exit(' ')

# -------------------------------
if __name__ == "__main__":
    main()
