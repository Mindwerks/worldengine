"""
This file is supposed to be the wrapper around image-processing modules like
PyPNG or Pillow. These modules should not be included anywhere but here. Should
a later replacement be necessary, it should be easy to do.
This module provides elaborate means to write images and simple means to read
them, too - the latter is (currently) only needed for the tests to be able to
run, hence a rudimentary implementation should suffice.

The arrays in WorldEngine are numpy-arrays and thus use matrix-notation for
access, see: https://en.wikipedia.org/wiki/Matrix_%28mathematics%29
This means that a matrix-element will be accessed via [y, x] throughout the
code.
Only right before writing (PNGWriter.complete()) and right after reading
(PNGReader.__init__()) may there be a need to switch to [x, y]-notation, but it
can probably be avoided even then.

In case the used library was replaced, the following functions have to be
rewritten:
  PNGWriter.complete()
  PNGWriter.prepare_array()
  PNGReader.__init__()
"""

import numpy
import png
#Documentation PyPNG: https://pythonhosted.org/pypng/png.html
#Documentation PurePNG: http://purepng.readthedocs.org/en/latest/
#The latter one is a fork of the former one. It is yet to be seen which one is better.


class PNGWriter(object):
    """
    From https://pythonhosted.org/pypng/png.html#module-png :
    -reads/writes PNG files with all allowable bit depths: 1/2/4/8/16/24/32/48/64
    -colour combinations:
        greyscale (1/2/4/8/16 bit)
        RGB, RGBA
        LA (greyscale with alpha) with 8/16 bits per channel
        colour mapped images (1/2/4/8 bit)
    """
    # convenience constructors
    @staticmethod
    def grayscale_from_dimensions(width, height, filename=None, channel_bitdepth=16):
        return PNGWriter.from_dimensions(width, height, channels=1, filename=filename,
                                         channel_bitdepth=channel_bitdepth, grayscale=True)

    @staticmethod
    def rgb_from_dimensions(width, height, filename=None, channel_bitdepth=8):
        return PNGWriter.from_dimensions(width, height, channels=3, filename=filename,
                                         channel_bitdepth=channel_bitdepth)

    @staticmethod
    def rgba_from_dimensions(width, height, filename=None, channel_bitdepth=8):
        return PNGWriter.from_dimensions(width, height, channels=4, filename=filename,
                                         channel_bitdepth=channel_bitdepth, has_alpha=True)

    @staticmethod
    def grayscale_from_array(array, filename=None, channel_bitdepth=16, scale_to_range=False):
        return PNGWriter.from_array(array, filename=filename, channels=1, scale_to_range=scale_to_range,
                                    grayscale=True, channel_bitdepth=channel_bitdepth)

    @staticmethod
    def rgb_from_array(array, filename=None, channel_bitdepth=8, scale_to_range=False):
        return PNGWriter.from_array(array, filename=filename, channels=3, scale_to_range=scale_to_range,
                                    channel_bitdepth=channel_bitdepth)

    @staticmethod
    def rgba_from_array(array, filename=None, channel_bitdepth=8, scale_to_range=False):
        return PNGWriter.from_array(array, filename=filename, channels=4, scale_to_range=scale_to_range,
                                    channel_bitdepth=channel_bitdepth, has_alpha=True)

    # general constructors
    def __init__(self, array, filename=None, channels=3, channel_bitdepth=8, has_alpha=False, palette=None, grayscale=False):
        """
        Calling the generic constructor gives full control over the created PNG
        file but it is very much recommended to use the appropriate static
        constructors instead (or add one if it is missing).
        
        The default settings are chosen to represent a standard RGB image.
        """
        self.img = None
        self.array = array
        self.filename = filename
        self.channels = channels

        # PNG parameters
        self.height = array.shape[0]
        self.width = array.shape[1]
        self.grayscale = grayscale
        self.channel_bitdepth = channel_bitdepth
        self.has_alpha = has_alpha
        self.palette = palette

    @classmethod
    def from_dimensions(cls, width, height, channels, filename=None,
                        grayscale=False, channel_bitdepth=8,
                        has_alpha=False, palette=None):
        """
        Creates an empty image according to width, height and channels.
        Channels must be 1 (grayscale/palette), 2 (LA), 3 (RGB) or 4 (RGBA).
        The image will be filled with black, transparent pixels.
        """
        assert 1 <= channels <= 4, "PNG only supports 1 to 4 channels per pixel. Error writing %s." % filename

        dimensions = (height, width, channels)
        if channels == 1:
            dimensions = (height, width)  # keep the array 2-dimensional when possible

        _array = numpy.zeros(dimensions, dtype=PNGWriter.get_dtype(channel_bitdepth))
        return cls(_array, filename,
                   grayscale=grayscale, channel_bitdepth=channel_bitdepth,
                   has_alpha=has_alpha, palette=palette, channels=channels)

    @classmethod
    def from_array(cls, array, filename=None, channels=3, scale_to_range=False,
                   grayscale=False, channel_bitdepth=8,
                   has_alpha=False, palette=None):
        """
        Creates an image by using a provided array. The array may be ready to
        be written or still need fine-tuning via set_pixel().
        The array should not have more than 3 dimensions or the output might be
        unexpected.
        """
        if scale_to_range:
            amax = array.max()
            amin = array.min()
            _array = (2**channel_bitdepth - 1) * (array - amin) / (amax - amin)
        else:
            _array = array
        _array = numpy.rint(_array).astype(dtype=PNGWriter.get_dtype(channel_bitdepth))  # proper rounding
        return cls(_array, filename, channels=channels,
                   grayscale=grayscale, channel_bitdepth=channel_bitdepth,
                   has_alpha=has_alpha, palette=palette)

    #the following methods should not need to be overriden
    def set_pixel(self, x, y, color):
        """
        Color may be: value, tuple, list etc.

        If the image is set to contain more color-channels than len(color), the
        remaining channels will be filled automatically.
        Example (channels = 4, i.e. RGBA output):
          color = 17 -> color = [17,17,17,255]
          color = (17, 99) -> color = [17,99,0,255]

        Passing in shorthand color-tuples for larger images on a regular basis
        might result in a very noticeable performance penalty.
        """
        try:  # these checks are for convenience, not for safety
            if len(color) < self.channels:  # color is a a tuple (length >= 1)
                if len(color) == 1:
                    if self.channels == 2:
                        color = [color[0], 255]
                    elif self.channels == 3:
                        color = [color[0], color[0], color[0]]
                    elif self.channels == 4:
                        color = [color[0], color[0], color[0], 255]
                elif len(color) == 2:
                    if self.channels == 3:
                        color = [color[0], color[1], 0]
                    elif self.channels == 4:
                        color = [color[0], color[1], 0, 255]
                elif len(color) == 3:
                    if self.channels == 4:
                        color = [color[0], color[1], color[2], 255]
        except TypeError:  # color is not an iterable
            if self.channels > 1:
                if self.channels == 2:
                    color = [color, 255]
                elif self.channels == 3:
                    color = [color, color, color]
                else:  # only values 1..4 are allowed
                    color = [color, color, color, 255]
        self.array[y, x] = color

    def complete(self, filename=None):
        if filename is None:
            filename = self.filename
        if filename is None:
            return
        if self.img is None:
            self.img = png.Writer(width=self.width, height=self.height,
                                  greyscale=self.grayscale, bitdepth=self.channel_bitdepth,  # British spelling
                                  alpha=self.has_alpha, palette=self.palette)
        #write the image
        with open(filename, 'wb') as f:
            self.img.write_array(f, self.prepare_array(self.array))

    @staticmethod
    def get_dtype(channel_bitdepth):
        #PNG uses unsigned data exclusively; max. 16 Bit per channel
        if 8 < channel_bitdepth <= 16:
            return numpy.uint16
        return numpy.uint8

    @staticmethod
    def prepare_array(array):
        """
        From https://pythonhosted.org/pypng/png.html#module-png :
        -for an image 3 pixels wide by 2 pixels high, each pixel has RGB components:
        "boxed row flat pixel"  - list(  [R,G,B,   R,G,B,   R,G,B],
                                         [R,G,B,   R,G,B,   R,G,B])
        "flat row flat pixel"   - list(  [R,G,B,   R,G,B,   R,G,B,
                                          R,G,B,   R,G,B,   R,G,B])
        "boxed row boxed pixel" - list([ (R,G,B), (R,G,B), (R,G,B) ],
                                       [ (R,G,B), (R,G,B), (R,G,B) ])
        -top row first, for each row pixels are ordered left-to-right
        -within a pixel values appear in the order R-G-B-A (or L-A for greyscale alpha)

        -corresponding numpy.ndarray.shape: (height, width, channels), e.g. (2, 3, 3)

        return: array in one of these formats ("boxed row boxed pixel"
                supposedly uses a lot of memory)
        """
        return array.flatten('C').tolist()

    def get_max_colors(self):
        return 2**self.channel_bitdepth - 1

    def __getitem__(self, item):
        return self.array[item]

    def __setitem__(self, item, value):
        self.array[item] = value


class PNGReader(object):
    def __init__(self, filename):
        self.filename = filename

        reader = png.Reader(filename=filename)
        pngdata = reader.asDirect()  # returns (width, height, pixels, meta), pixels as 'boxed row, flat pixel'

        self.width = pngdata[0]
        self.height = pngdata[1]

        self.array = numpy.vstack(map(numpy.uint16, pngdata[2]))  # creates a 2-dimensional array (flat pixels)
        if pngdata[3]['planes'] > 1:  # 'unflatten' the pixels
            self.array = self.array.reshape(self.height, self.width, -1)  # height, width, depth (-1 = automatic)

    def __getitem__(self, item):
        return self.array[item]

    def __eq__(self, other):
        #palettes do not need to be compared since asDirect() automatically maps the pixels to their colors
        return numpy.array_equiv(self.array, other.array)
