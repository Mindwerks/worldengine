#external
import sys

import argparse

import numpy
import os

#from this package
import worldengine

from worldengine.common import set_verbose
from worldengine.step import Step
from worldengine.version import __version__


VERSION = __version__

OPERATIONS = 'world|plates|ancient_map|info|export'
SEA_COLORS = 'blue|brown'
STEPS = 'plates|precipitations|full'





def check_step(step_name):
    step = Step.get_by_name(step_name)
    if step is None:
        print("ERROR: unknown step name, using default 'full'")
        return Step.get_by_name("full")
    else:
        return step

def __get_last_byte__(filename):
    #why does this exist?
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
    tag = __get_tag__(world_filename)
    return tag == worldengine.world.World.worldengine_tag()



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

def value_parsing_arguments(parser):
    
    parser.add_argument('-x', '--width', dest='width', type=int,
                        help="N = width of the world to be generated " +
                             "[default=%(default)s]",
                        metavar="N",
                        default='512')
    
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
    
    parser.add_argument('-y', '--height', dest='height', type=int,
                        help="N = height of the world to be generated " +
                             "[default=%(default)s]",
                        metavar="N",
                        default='512')
    parser.add_argument('-q', '--number-of-plates', dest='number_of_plates',
                        type=int,
                        help="N = number of plates [default = %(default)s]",
                        metavar="N", default='10')
    
    parser.add_argument('--temps', dest='temps',
                            help="Provide alternate ranges for temperatures. " +
                                 "If not provided, the default values will be used. \n" +
                                 "[default = .126/.235/.406/.561/.634/.876]",
                            metavar="#/#/#/#/#/#")
                            
    parser.add_argument('--humidity', dest='humids',
                            help="Provide alternate ranges for humidities. " +
                                 "If not provided, the default values will be used. \n" +
                                 "[default = .059/.222/.493/.764/.927/.986/.998]",
                            metavar="#/#/#/#/#/#/#")
                        
def operation_parsing_arguments(parser):
    parser.add_argument('OPERATOR', nargs='?')
    
    
    parser.add_argument('-t', '--step', dest='step',
                        help="Use step=[" + STEPS + "] to specify how far " +
                             "to proceed in the world generation process. " +
                             "[default='%(default)s']",
                        metavar="STR", default="full")
    # TODO --step appears to be duplicate of OPERATIONS. Especially if
    # ancient_map is added to --step
    
def input_parsing_arguments(parser):
    
    parser.add_argument('FILE', nargs='?')
    
    
    parser.add_argument('--version', dest='version', action="store_true",
                        help="Display version information", default=False)
    
    
    parser.add_argument('--recursion_limit', dest='recursion_limit', type=int,
                        help="Set the recursion limit [default = %(default)s]",
                        metavar="N", default='2000')
    
def output_options_parsing(parser):
    
    
    parser.add_argument(
        '-o', '--output-dir', dest='output_dir',
        help="generate files in DIR [default = '%(default)s']",
        metavar="DIR", default='.')
        
    parser.add_argument('--hdf5', dest='hdf5',
                        action="store_true",
                        help="Save world file using HDF5 format. " +
                             "Default = store using protobuf format",
                        default=False)
    
    parser.add_argument('-v', '--verbose', dest='verbose', action="store_true",
                        help="Enable verbose messages", default=False)
    
    
    parser.add_argument('--bw', '--black-and-white', dest='black_and_white',
                        action="store_true",
                        help="generate maps in black and white",
                        default=False)
                        
    
    
    #these have to be split.
    #there is stuff that relates to output and stuff that relations to generation.
    
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
                            
                            
    g_generate.add_argument('--not-fade-borders', dest='fade_borders', action="store_false",
                            help="Not fade borders",
                            default=True)
    
    
    g_generate.add_argument('-gv', '--gamma-value', dest='gv', type=float,
                            help="N = Gamma value for temperature/precipitation " +
                                 "gamma correction curve. [default = %(default)s]",
                            metavar="N", default='1.25')
                            
    g_generate.add_argument('-go', '--gamma-offset', dest='go', type=float,
                            help="N = Adjustment value for temperature/precipitation " +
                                 "gamma correction curve. [default = %(default)s]",
                            metavar="N", default='.2')
    
    g_generate.add_argument('--scatter', dest='scatter_plot',
                            action="store_true", help="generate scatter plot")
                            
    g_generate.add_argument('--sat', dest='satelite_map',
                            action="store_true", help="generate satellite map")
                            
    g_generate.add_argument('--ice', dest='icecaps_map',
                            action="store_true", help="generate ice caps map")
    
    
    # -----------------------------------------------------
    export_options = parser.add_argument_group(
        "Export Options", "You can specify the formats you wish the generated output to be in. ")
    export_options.add_argument("--export-format", dest="export_format", type=str,
                                help="Export to a specific format such as BMP or PNG. " +
                                     "All possible formats: http://www.gdal.org/formats_list.html",
                                default="PNG", metavar="STR")
    export_options.add_argument("--export-datatype", dest="export_datatype", type=str,
                                help="Type of stored data (e.g. uint16, int32, float32 and etc.)",
                                default="uint16", metavar="STR")
    export_options.add_argument("--export-dimensions", dest="export_dimensions", type=int,
                                help="Export to desired dimensions. (e.g. 4096 4096)", default=None,
                                nargs=2)
    export_options.add_argument("--export-normalize", dest="export_normalize", type=int,
                                help="Normalize the data set to between min and max. (e.g 0 255)",
                                nargs=2, default=None)
    export_options.add_argument("--export-subset", dest="export_subset", type=int,
                                help="Normalize the data set to between min and max?",
                                nargs=4, default=None)

def ancient_map_options(parser):
    
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

    

def arg_parsing():
    
    parser = argparse.ArgumentParser(
        usage="usage: %(prog)s [options] [" + OPERATIONS + "]")
    
    #these should be generation inputs for the generation operations
    value_parsing_arguments(parser)
    
    #these are the inputs about the *kind* of generation operation
    operation_parsing_arguments(parser)
    
    #this is other stuff, like the data file to use
    input_parsing_arguments(parser)
    
    #this handles the desired output and formatting, exports, etc.
    output_options_parsing(parser)
    
    ancient_map_options(parser)
    

    
    #parse everthing
    
    args = parser.parse_args()
    arg_dict=vars(args)
    
    #defaulthing them
    arg_dict["save"]=True
    arg_dict["draw"]=True
    
    if args.version:
        usage()
        
    return args,arg_dict

def main():
    #this is just a fancy parser.
    p=proto_world()
    return p.main()

class proto_world:
    def arg_errors(self,args):
        
        if os.path.exists(args.output_dir):
            if not os.path.isdir(args.output_dir):
                raise Exception("Output dir exists but it is not a dir")
        else:
            print('Directory does not exist, we are creating it')
            os.makedirs(args.output_dir)
        
        
        if args.number_of_plates < 1 or args.number_of_plates > 100:
            usage(error="Number of plates should be in [1, 100]")

        if args.OPERATOR == 'info' or args.OPERATOR == 'export':
            if args.FILE is None:
                usage("For operation info only the filename should be specified")
            if not os.path.exists(args.FILE):
                usage("The specified world file does not exist")
        
        
        if args.go >= 1 or args.go < 0:
            usage(error="Gamma offset must be greater than or equal to 0 and less than 1")

        if args.gv <= 0:
            usage(error="Gamma value must be greater than 0")
        
        # Warning messages
        temps=self.arg_dict["temps"]
        humids=self.arg_dict["humids"]
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
        
        ##more warnings? hm.
        #if False:#
            ##these are nonsense. let people do whatever. won't change the output.

            #if args.grayscale_heightmap:
                #usage(
                    #error="Grayscale heightmap can be produced only during world " +
                          #"generation")

            #if args.rivers_map:
                #usage(error="Rivers map can be produced only during world generation")

            #if args.temps:
                #usage(error="temps can be assigned only during world generation")

            #if args.humids:
                #usage(error="humidity can be assigned only during world generation")
        
            #if args.scatter_plot:
                #usage(error="Scatter plot can be produced only during world generation")
    
    
        
    def set_humids(self,args):
        #preeeetty sure this can cause some
        #problems if bad values are supplied.
        humids = [.941, .778, .507, .236, 0.073, .014, .002]
        if args.humids:
            humids = args.humids.split('/')
            if len(humids) is not 7:
                usage(error="humidity must have exactly 7 values")
            for x in range(0, len(humids)):
                humids[x] = 1 - float(humids[x])
                
        self.arg_dict["humids"]=humids
    
    

    def set_seed(self,args):
        # there is a hard limit somewhere so seeds outside the uint16 range are considered unsafe
        maxseed = numpy.iinfo(numpy.uint16).max
        #seed 
        if args.seed is not None:
            seed = int(args.seed)
            assert 0 <= seed <= maxseed, \
                "Seed has to be in the range between 0 and %s, borders included." % maxseed
        else:
              # first-time RNG initialization is done automatically
        
            seed = numpy.random.randint(0,maxseed)
            numpy.random.seed(seed)
            
        self.arg_dict["seed"]=seed

    def set_temps(self,args):
        
        temps = [.874, .765, .594, .439, .366, .124]
        if args.temps:
            
            temps = args.temps.split('/')
            
            if len (temps) != 6:
                usage(error="temps must have exactly 6 values")

            for x in range(0, len(temps)):
                temps[x] = 1 - float(temps[x])
                
        self.arg_dict["temps"]=temps

    def set_operation(self,args):
        operation = "world"
        if args.OPERATOR is None:
            pass
        elif args.OPERATOR is not None and args.OPERATOR.lower() not in OPERATIONS:
            
            usage("Only 1 operation allowed [" + OPERATIONS + "]")
        else:
            operation = args.OPERATOR.lower()
            
        generation_operation = (operation == 'world') or (operation == 'plates')
        
        self.arg_dict["generation_operation"]=generation_operation
        self.arg_dict["operation"]=operation

    def set_world_name(self,args):
        
        if args.world_name:
            world_name = args.world_name
        else:
            world_name = "seed_%i" % self.arg_dict["seed"]
        self.arg_dict["world_name"]=world_name

    def set_world_format(self,args):
        #this seems like more input and format stuff.
        
        world_format = 'protobuf'
        if args.hdf5:
            world_format = 'hdf5'
            
        self.arg_dict["world_format"]=world_format
    
    
    def main(self):
        
        args,arg_dict=arg_parsing()
        
        self.arg_dict=arg_dict
        
        #arg handling
        
        sys.setrecursionlimit(args.recursion_limit)
        #I'm sorry but the default is 1000. What are you doing that you need that
        #deep recursion for?
        
        #set the options from parsed arguments
        
        #plates or world
        self.set_operation(args)
        self.set_seed(args)
        self.set_world_name(args)    
        self.set_world_format(args)
        self.set_temps(args)
        self.set_humids(args)

        #this is the generation step 
        step = check_step(args.step)
        self.arg_dict["step"]=step
        
        self.arg_errors(args)
        
        # it needs to be increased to be able to generate very large maps
        # recursion limit the limit is hit when drawing ancient maps
        
        #this is print() output.
        
        self.normal_print(args)
        
        #this relates to output. I assume it's printing during generation?
        set_verbose(args.verbose)

        print('...done')
        return args,arg_dict


    def normal_print(self,args):
        generation_operation=self.arg_dict["generation_operation"]
        operation=self.arg_dict["operation"]
        seed=self.arg_dict["seed"]
        world_name=self.arg_dict["world_name"]
        world_format=self.arg_dict["world_format"]
        step=self.arg_dict["step"]
        
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
            print(' icecaps heightmap    : %s' % args.icecaps_map)
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

    

def usage(error=None):
    print(
        ' -------------------------------------------------------------------')
    print(' Federico Tomassetti and Bret Curtis, 2011-2017')
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


