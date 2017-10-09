import sys
import numpy

# ----------------
# Global variables
# ----------------


verbose = False


# -------
# Functions
# -------


def get_verbose():
    global verbose
    if 'verbose' not in globals():
        return False
    else:
        return verbose


def set_verbose(value):
    """
    Set the level of verbosity for all the operations executed in Worldengine
    """
    global verbose
    verbose = value


def print_verbose(msg):
    if get_verbose():
        print(msg)


class Counter(object):

    def __init__(self):
        self.c = {}

    def count(self, what):
        if what not in self.c:
            self.c[what] = 0
        self.c[what] += 1

    def to_str(self):
        string = ""
        keys = sorted(self.c.keys())
        for w in keys:
            string += "%s : %i" % (w, self.c[w])
            string += "\n"
        return string

    def print_self(self):
        # print without the new line
        sys.stdout.write(self.to_str)


# For each step and each x, y the original implementation averaged 
# over the 9 values in the square from (x-1, y-1) to (x+1,y+1)
# To that it added, with equal weight, twice the initial value.
# That makes a total of 11 values.
# Therefore the original implementation is equivalent to this convolution:
#
# current = map
#
# map_part = (2/11)*map
    
# linear_filter = [[1/11, 1/11, 1/11],
#                  [1/11, 1/11, 1/11],
#                  [1/11, 1/11, 1/11]]

# for i in range(steps):
#   current = signal.convolve2d(current, linear_filter, mode='same', boundary='wrap') + map_part
# return current
#
#
# Unless we want to add scipy as a dependency we only have 1D convolution at our hands from numpy.
# So we take advantage of the kernel being seperable.

def anti_alias(map_in, steps):
    """
    Execute the anti_alias operation steps times on the given map
    """

    height, width = map_in.shape

    map_part = (2.0/11.0)*map_in

    # notice how [-1/sqrt(3), -1/sqrt(3), -1/sqrt(3)] * [-1/sqrt(3), -1/sqrt(3), -1/sqrt(3)]^T
    # equals [[1/3, 1/3, 1/3], [1/3, 1/3, 1/3], [1/3, 1/3, 1/3]]
    # multiply that by (3/11) and we have the 2d kernel from the example above
    # therefore the kernel is seperable

    w = -1.0/numpy.sqrt(3.0)
    kernel = [w, w, w]

    def _anti_alias_step(original):

        # cf. comments above fo the factor
        # this also makes a copy which might actually be superfluous
        result = original * (3.0/11.0)

        # we need to handle boundary conditions by hand, unfortunately
        # there might be a better way but this works (circular boundary)
        # notice how we'll need to add 2 to width and height later 
        # because of this
        result = numpy.append(result, [result[0,:]], 0)
        result = numpy.append(result, numpy.transpose([result[:,0]]), 1)

        result = numpy.insert(result, [0], [result[-2,:]],0)
        result = numpy.insert(result, [0], numpy.transpose([result[:,-2]]), 1)

        # with a seperable kernel we can convolve the rows first ...
        for y in range(height+2):
            result[y,1:-1] = numpy.convolve(result[y,:], kernel, 'valid')

        # ... and then the columns
        for x in range(width+2):
            result[1:-1,x] = numpy.convolve(result[:,x], kernel, 'valid')

        # throw away invalid values at the boundary
        result = result[1:-1,1:-1]

        result += map_part

        return result

    current = map_in
    for i in range(steps):
        current = _anti_alias_step(current)
    return current

def count_neighbours(mask, radius=1):
    '''Count how many neighbours of a coordinate are set to one.
    This uses the same principles as anti_alias, compare comments there.'''

    height, width = mask.shape

    f = 2.0*radius+1.0

    w = -1.0/numpy.sqrt(f)
    kernel = [w]*radius + [w] + [w]*radius

    result = mask * f

    for y in range(height):
        result[y,:]  = numpy.convolve(result[y,:], kernel, 'same')

    for x in range(width):
        result[:,x] = numpy.convolve(result[:, x], kernel, 'same')

    return result - mask


def _equal(a, b):
    #recursion on subclasses of types: tuple, list, dict
    #specifically checks             : float, ndarray
    if type(a) is float and type(b) is float:#float
        return(numpy.allclose(a, b))
    elif type(a) is numpy.ndarray and type(b) is numpy.ndarray:#ndarray
        return(numpy.array_equiv(a, b))#alternative for float-arrays: numpy.allclose(a, b[, rtol, atol])
    elif isinstance(a, dict) and isinstance(b, dict):#dict
        if len(a) != len(b):
            return(False)
        t = True
        for key, val in a.items():
            if key not in b:
                return(False)
            t = _equal(val, b[key])
            if not t:
                return(False)
        return(t)
    elif (isinstance(a, list) and isinstance(b, list)) or (isinstance(a, tuple) and isinstance(b, tuple)):#list, tuples
        if len(a) != len(b):
            return(False)
        t = True
        for vala, valb in zip(a, b):
            t = _equal(vala, valb)
            if not t:
                return(False)
        return(t)
    else:#fallback
        return (a == b)
