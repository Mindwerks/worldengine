import sys
import copy

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
        keys = self.c.keys()
        keys.sort()
        for w in keys:
            string += "%s : %i" % (w, self.c[w])
            string += "\n"
        return string

    def print_self(self):
        # print without the new line
        sys.stdout.write(self.to_str)


def matrix_min_and_max(matrix):
    _min = None
    _max = None
    for row in matrix:
        for el in row:
            val = el
            if _min is None or val < _min:
                _min = val
            if _max is None or val > _max:
                _max = val
    return _min, _max


def rescale_value(original, prev_min, prev_max, min, max):
    """Rescale a given value.
    Given the value, the current min and max and the new min and max
    produce the rescaled value
    """
    f = float(original - prev_min) / (prev_max - prev_min)
    return min + ((max - min) * f)


def anti_alias(elevation, steps):
    """
    Execute the anti_alias operation steps times on the given elevation map
    """
    width = len(elevation[0])
    height = len(elevation)

    def _anti_alias_step(original):
        anti_aliased = copy.deepcopy(original)
        for y in range(height):
            for x in range(width):
                anti_aliased[y][x] = anti_alias_point(original, x, y)
        return anti_aliased

    def anti_alias_point(original, x, y):
        n = 2
        tot = elevation[y][x] * 2
        for dy in range(-1, +2):
            py = (y + dy) % height
            for dx in range(-1, +2):
                px = (x + dx) % width
                n += 1
                tot += original[py][px]
        return tot / n

    current = elevation
    for i in range(steps):
        current = _anti_alias_step(current)
    return current


def array_to_matrix(array, width, height):
    if len(array) != (width * height):
        raise Exception("Array as not expected length")
    matrix = []
    for y in xrange(height):
        matrix.append([])
        for x in xrange(width):
            matrix[y].append(array[y * width + x])
    return matrix
