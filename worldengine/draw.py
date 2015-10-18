from PIL import Image
import numpy
import png
#Documentation PyPNG: https://pythonhosted.org/pypng/png.html
#Documentation PurePNG: http://purepng.readthedocs.org/en/latest/
#The latter one is a fork of the former one. Don't know which is better, but one will hopefully survive for a long time. :P

from worldengine.drawing_functions import draw_ancientmap, \
    draw_rivers_on_image, gradient

# -------------
# Helper values
# -------------

_biome_colors = {
    'ocean': (23, 94, 145),
    'sea': (23, 94, 145),
    'ice': (255, 255, 255),
    'subpolar dry tundra': (128, 128, 128),
    'subpolar moist tundra': (96, 128, 128),
    'subpolar wet tundra': (64, 128, 128),
    'subpolar rain tundra': (32, 128, 192),
    'polar desert': (192, 192, 192),
    'boreal desert': (160, 160, 128),
    'cool temperate desert': (192, 192, 128),
    'warm temperate desert': (224, 224, 128),
    'subtropical desert': (240, 240, 128),
    'tropical desert': (255, 255, 128),
    'boreal rain forest': (32, 160, 192),
    'cool temperate rain forest': (32, 192, 192),
    'warm temperate rain forest': (32, 224, 192),
    'subtropical rain forest': (32, 240, 176),
    'tropical rain forest': (32, 255, 160),
    'boreal wet forest': (64, 160, 144),
    'cool temperate wet forest': (64, 192, 144),
    'warm temperate wet forest': (64, 224, 144),
    'subtropical wet forest': (64, 240, 144),
    'tropical wet forest': (64, 255, 144),
    'boreal moist forest': (96, 160, 128),
    'cool temperate moist forest': (96, 192, 128),
    'warm temperate moist forest': (96, 224, 128),
    'subtropical moist forest': (96, 240, 128),
    'tropical moist forest': (96, 255, 128),
    'warm temperate dry forest': (128, 224, 128),
    'subtropical dry forest': (128, 240, 128),
    'tropical dry forest': (128, 255, 128),
    'boreal dry scrub': (128, 160, 128),
    'cool temperate desert scrub': (160, 192, 128),
    'warm temperate desert scrub': (192, 224, 128),
    'subtropical desert scrub': (208, 240, 128),
    'tropical desert scrub': (224, 255, 128),
    'cool temperate steppe': (128, 192, 128),
    'warm temperate thorn scrub': (160, 224, 128),
    'subtropical thorn woodland': (176, 240, 128),
    'tropical thorn woodland': (192, 255, 128),
    'tropical very dry forest': (160, 255, 128),
}

# ----------------
# Helper functions
# ----------------


def _elevation_color(elevation, sea_level=1.0):
    """
    Calculate color based on elevation
    :param elevation:
    :return:
    """
    color_step = 1.5
    if elevation < sea_level/2:
        elevation /= sea_level
        return 0.0, 0.0, 0.75 + 0.5 * elevation
    elif elevation < sea_level:
        elevation /= sea_level
        return 0.0, 2 * (elevation - 0.5), 1.0
    else:
        elevation -= sea_level
        if elevation < 1.0 * color_step:
            return (0.0, 0.5 +
                    0.5 * elevation / color_step, 0.0)
        elif elevation < 1.5 * color_step:
            return 2 * (elevation - 1.0 * color_step) / color_step, 1.0, 0.0
        elif elevation < 2.0 * color_step:
            return 1.0, 1.0 - (elevation - 1.5 * color_step) / color_step, 0
        elif elevation < 3.0 * color_step:
            return (1.0 - 0.5 * (elevation - 2.0 *
                                 color_step) / color_step,
                    0.5 - 0.25 * (elevation - 2.0 *
                                  color_step) / color_step, 0)
        elif elevation < 5.0 * color_step:
            return (0.5 - 0.125 * (elevation - 3.0 *
                                   color_step) / (2 * color_step),
                    0.25 + 0.125 * (elevation - 3.0 *
                                    color_step) / (2 * color_step),
                    0.375 * (elevation - 3.0 *
                             color_step) / (2 * color_step))
        elif elevation < 8.0 * color_step:
            return (0.375 + 0.625 * (elevation - 5.0 *
                                     color_step) / (3 * color_step),
                    0.375 + 0.625 * (elevation - 5.0 *
                                     color_step) / (3 * color_step),
                    0.375 + 0.625 * (elevation - 5.0 *
                                     color_step) / (3 * color_step))
        else:
            elevation -= 8.0 * color_step
            while elevation > 2.0 * color_step:
                elevation -= 2.0 * color_step
            return 1, 1 - elevation / 4.0, 1


def _sature_color(color):
    r, g, b = color
    if r < 0:
        r = 0.0
    if r > 1.0:
        r = 1.0
    if g < 0:
        g = 0.0
    if g > 1.0:
        g = 1.0
    if b < 0:
        b = 0.0
    if b > 1.0:
        b = 1.0
    return r, g, b


def elevation_color(elevation, sea_level=1.0):
    return _sature_color(_elevation_color(elevation, sea_level))


# ----------------------
# Draw on generic target
# ----------------------

class MapToPNGPrinter(object):
    def __init__(self, map, filename, grayscale = True):#TODO: currently only works for 16 bit grayscale, might want to adapt it to other specifications; PyPNG supposedly can handle them all
        self.img = png.Writer(width = map.shape[1], height = map.shape[0], greyscale = grayscale, bitdepth = 16)#British spelling
        self.map = map
        self.filename = filename
        self.grayscale = grayscale

    @classmethod
    def from_dimensions(cls, width, height, filename, grayscale = True):
        _map = numpy.zeros((height, width), dtype = numpy.uint16)
        return cls(_map, filename, grayscale)

    @classmethod
    def from_map(cls, map, filename, grayscale = True, scale_to_range = True):
        if scale_to_range:
            max = map.max()
            min = map.min()
            _map = (2**16 - 1) * (map - min) / (max - min)
        _map = _map.astype(dtype = numpy.uint16)
        return cls(_map, filename, grayscale)

    def set_pixel(self, x, y, color):#TODO: currently only works for 16 bit grayscale
        self.map[y, x] = color

    def complete(self):
        with open(self.filename, 'wb') as f:
            out = self.map.tolist()#convert to Python list of lists as expected by the png-writer
            self.img.write(f, out)

    def __getitem__(self, item):
        return self.map[item]

    def __setitem__(self, item, value):
        self.map[item] = value


class ImagePixelSetter(object):#TODO: right now only works for colored images, can probably be combined with MapToPNGPrinter-class

    def __init__(self, width, height, filename):
        self.img = Image.new('RGBA', (width, height))
        self.pixels = self.img.load()
        self.filename = filename

    def set_pixel(self, x, y, color):
        if len(color) == 3:  # Convert RGB to RGBA - TODO: go through code to fix this
            color = (color[0], color[1], color[2], 255)
        self.pixels[x, y] = color

    def complete(self):
        try:
            self.img.save(self.filename)
        except KeyError:
            print("Cannot save to file `{}`, unsupported file format.".format(self.filename))
            filename = self.filename+".png"
            print("Defaulting to PNG: `{}`".format(filename))
            self.img.save(filename)

    def __getitem__(self, item):
        return self.pixels[item]

    def __setitem__(self, item, value):
        if len(value) == 3:  # Convert RGB to RGBA - TODO: go through code to fix this
            value = (value[0], value[1], value[2], 255)
        self.pixels[item] = value


def draw_simple_elevation(data, width, height, sea_level, target):
    """ This function can be used on a generic canvas (either an image to save
        on disk or a canvas part of a GUI)
    """
    for y in range(height):
        for x in range(width):
            e = data[y, x]
            r, g, b = elevation_color(e, sea_level)
            target.set_pixel(x, y, (int(r * 255), int(g * 255),
                                    int(b * 255), 255))


def draw_riversmap(world, target):
    sea_color = (255, 255, 255, 255)
    land_color = (0, 0, 0, 255)

    for y in range(world.height):
        for x in range(world.width):
            if world.ocean[y, x]:
                target.set_pixel(x, y, sea_color)
            else:
                target.set_pixel(x, y, land_color)

    draw_rivers_on_image(world, target, factor=1)


def draw_grayscale_heightmap(world, target):
    #target: ImagePixelSetter object (writes 8 Bit grayscale)
    mask = numpy.ma.array(world.elevation['data'], mask = world.ocean)
    min_elev_land = mask.min()
    max_elev_land = mask.max()
    
    mask.mask = numpy.logical_not(mask.mask)
    min_elev_sea = mask.min()
    max_elev_sea = mask.max()
    
    elev_delta_land = max_elev_land - min_elev_land
    elev_delta_sea = max_elev_sea - min_elev_sea
    
    total_min = world.elevation['data'].min()
    total_max = world.elevation['data'].max()
    elev_delta = total_max - total_min

    bpp = 8
    printer = False
    if type(target) is MapToPNGPrinter:
        bpp = 16
        printer = True
    halfcol = 2**(bpp - 1) - 1

    for y in range(world.height):
        for x in range(world.width):
            e = world.elevation['data'][y, x]
            '''This comment is just for clarification and should be removed soon.
            Note: The previous method (in comments) does not allow for true
            depressions in the output *and* if depressions existed in the input,
            the landmass will be lifted up, creating very unrealistic coasts.
            '''
            if world.is_land((x, y)):
                #c = int(halfcol * (e - min_elev_land) / elev_delta_land) + halfcol + 1
                c = int((2 * halfcol + 1) * (e - total_min) / elev_delta)
            else:
                #c = int(halfcol * (e - min_elev_sea) / elev_delta_sea)
                c = int((2 * halfcol + 1) * (e - total_min) / elev_delta)
            target.set_pixel(x, y, c if printer else (c, c, c))


def draw_elevation(world, shadow, target):
    width = world.width
    height = world.height

    data = world.elevation['data']
    ocean = world.ocean

    mask = numpy.ma.array(data, mask = ocean)

    min_elev = mask.min()
    max_elev = mask.max()
    elev_delta = max_elev - min_elev

    for y in range(height):
        for x in range(width):
            if ocean[y, x]:
                target.set_pixel(x, y, (0, 0, 255, 255))
            else:
                e = data[y, x]
                c = 255 - int(((e - min_elev) * 255) / elev_delta)
                if shadow and y > 2 and x > 2:
                    if data[y - 1, x - 1] > e:
                        c -= 15
                    if data[y - 2, x - 2] > e \
                            and data[y - 2, x - 2] > data[y - 1, x - 1]:
                        c -= 10
                    if data[y - 3, x - 3] > e \
                            and data[y - 3, x - 3] > data[y - 1, x - 1] \
                            and data[y - 3, x - 3] > data[y - 2, x - 2]:
                        c -= 5
                    if c < 0:
                        c = 0
                target.set_pixel(x, y, (c, c, c, 255))


def draw_ocean(ocean, target):
    height, width = ocean.shape

    for y in range(height):
        for x in range(width):
            if ocean[y, x]:
                target.set_pixel(x, y, (0, 0, 255, 255))
            else:
                target.set_pixel(x, y, (0, 255, 255, 255))


def draw_precipitation(world, target, black_and_white=False):
    #TODO: FIXME we are drawing humidity, not precipitations
    width = world.width
    height = world.height

    if black_and_white:
        floor = 0
        ceiling = 255
        if type(target) is MapToPNGPrinter:
            ceiling = 65535

        low = world.precipitation['data'].min()
        high = world.precipitation['data'].max()
        for y in range(height):#TODO: the following could easily be done on the whole array at once, but target might be of a type that cannot write a complete array
            for x in range(width):
                p = world.precipitations_at((x, y))
                c = numpy.interp(p, [low, high], [floor, ceiling])
                c = int(numpy.rint(c))#proper rounding
                target.set_pixel(x, y, c if ceiling == 65535 else (c, c, c))
    else:
        for y in range(height):
            for x in range(width):
                if world.is_humidity_superarid((x, y)):
                    target.set_pixel(x, y, (0, 32, 32, 255))
                elif world.is_humidity_perarid((x, y)):
                    target.set_pixel(x, y, (0, 64, 64, 255))
                elif world.is_humidity_arid((x, y)):
                    target.set_pixel(x, y, (0, 96, 96, 255))
                elif world.is_humidity_semiarid((x, y)):
                    target.set_pixel(x, y, (0, 128, 128, 255))
                elif world.is_humidity_subhumid((x, y)):
                    target.set_pixel(x, y, (0, 160, 160, 255))
                elif world.is_humidity_humid((x, y)):
                    target.set_pixel(x, y, (0, 192, 192, 255))
                elif world.is_humidity_perhumid((x, y)):
                    target.set_pixel(x, y, (0, 224, 224, 255))
                elif world.is_humidity_superhumid((x, y)):
                    target.set_pixel(x, y, (0, 255, 255, 255))


def draw_world(world, target):
    width = world.width
    height = world.height

    for y in range(height):
        for x in range(width):
            if world.is_land((x, y)):
                biome = world.biome_at((x, y))
                target.set_pixel(x, y, _biome_colors[biome.name()])
            else:
                c = int(world.sea_depth[y, x] * 200 + 50)
                target.set_pixel(x, y, (0, 0, 255 - c, 255))


def draw_temperature_levels(world, target, black_and_white=False):
    width = world.width
    height = world.height

    if black_and_white:
        floor = 0
        ceiling = 255
        if type(target) is MapToPNGPrinter:
            ceiling = 65535

        low = world.temperature_thresholds()[0][1]
        high = world.temperature_thresholds()[5][1]
        for y in range(height):#TODO: the following could easily be done on the whole array at once, but target might be of a type that cannot write a complete array
            for x in range(width):
                t = world.temperature_at((x, y))
                c = numpy.interp(t, [low, high], [floor, ceiling])
                c = int(numpy.rint(c))
                target.set_pixel(x, y, c if ceiling == 65535 else (c, c, c))

    else:
        for y in range(height):
            for x in range(width):
                if world.is_temperature_polar((x, y)):
                    target.set_pixel(x, y, (0, 0, 255, 255))
                elif world.is_temperature_alpine((x, y)):
                    target.set_pixel(x, y, (42, 0, 213, 255))
                elif world.is_temperature_boreal((x, y)):
                    target.set_pixel(x, y, (85, 0, 170, 255))
                elif world.is_temperature_cool((x, y)):
                    target.set_pixel(x, y, (128, 0, 128, 255))
                elif world.is_temperature_warm((x, y)):
                    target.set_pixel(x, y, (170, 0, 85, 255))
                elif world.is_temperature_subtropical((x, y)):
                    target.set_pixel(x, y, (213, 0, 42, 255))
                elif world.is_temperature_tropical((x, y)):
                    target.set_pixel(x, y, (255, 0, 0, 255))


def draw_biome(world, target):
    width = world.width
    height = world.height

    biome = world.biome

    for y in range(height):
        for x in range(width):
            v = biome[y, x]
            target.set_pixel(x, y, _biome_colors[v])


# -------------
# Draw on files
# -------------


def draw_simple_elevation_on_file(data, filename, width, height, sea_level):
    img = ImagePixelSetter(width, height, filename)
    draw_simple_elevation(data, width, height, sea_level, img)
    img.complete()


def draw_riversmap_on_file(world, filename):
    img = ImagePixelSetter(world.width, world.height, filename)
    draw_riversmap(world, img)
    img.complete()


def draw_grayscale_heightmap_on_file(world, filename):
    img = MapToPNGPrinter.from_map(world.elevation['data'], filename, grayscale = True, scale_to_range = True)
    #img = ImagePixelSetter(world.width, world.height, filename)
    #draw_grayscale_heightmap(world, img)
    img.complete()


def draw_elevation_on_file(world, filename, shadow=True):
    img = ImagePixelSetter(world.width, world.height, filename)
    draw_elevation(world, shadow, img)
    img.complete()


def draw_ocean_on_file(ocean, filename):
    img = ImagePixelSetter(ocean.shape[1], ocean.shape[0], filename)
    draw_ocean(ocean, img)
    img.complete()


def draw_precipitation_on_file(world, filename, black_and_white=False):#TODO: find out if 16 bit is appropriate for black_and_white output
    if black_and_white:
        img = MapToPNGPrinter.from_map(world.precipitation['data'], filename, grayscale = black_and_white, scale_to_range = True)
    else:
        img = ImagePixelSetter(world.width, world.height, filename)
    draw_precipitation(world, img, black_and_white)
    img.complete()


def draw_world_on_file(world, filename):
    img = ImagePixelSetter(world.width, world.height, filename)
    draw_world(world, img)
    img.complete()


def draw_temperature_levels_on_file(world, filename, black_and_white=False):#TODO: find out if 16 bit is appropriate for black_and_white output
    if black_and_white:
        img = MapToPNGPrinter.from_map(world.temperature['data'], filename, grayscale = black_and_white, scale_to_range = True)
    else:
        img = ImagePixelSetter(world.width, world.height, filename)
    draw_temperature_levels(world, img, black_and_white)
    img.complete()


def draw_biome_on_file(world, filename):
    img = ImagePixelSetter(world.width, world.height, filename)
    draw_biome(world, img)
    img.complete()


def draw_ancientmap_on_file(world, filename, resize_factor=1,
                            sea_color=(212, 198, 169, 255),
                            draw_biome=True, draw_rivers=True, draw_mountains=True, 
                            draw_outer_land_border=False, verbose=False):
    img = ImagePixelSetter(world.width * resize_factor,
                           world.height * resize_factor, filename)
    draw_ancientmap(world, img, resize_factor, sea_color,
                    draw_biome, draw_rivers, draw_mountains, draw_outer_land_border, 
                    verbose)
    img.complete()
