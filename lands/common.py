__author__ = 'Federico Tomassetti'

import math
import sys

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
    Set the level of verbosity for all the operations executed in Lands
    """
    global verbose
    verbose = value


class Counter(object):

    def __init__(self):
        self.c = {}

    def count(self, what):
        if what not in self.c:
            self.c[what] = 0
        self.c[what] += 1

    def to_str(self):
        str = ""
        keys = self.c.keys()
        keys.sort()
        for w in keys:
            str += "%s : %i" % (w, self.c[w])
            str += "\n"
        return str

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


# -------
# Scaling
# -------


def antialias(elevation, steps):
    width = len(elevation[0])
    height = len(elevation)

    def _antialias_step():
        for y in range(height):
            for x in range(width):
                antialias_point(x, y)

    def antialias_point(x, y):
        n = 2
        tot = elevation[y][x] * 2
        for dy in range(-1, +2):
            py = y + dy
            if py > 0 and py < height:
                for dx in range(-1, +2):
                    px = x + dx
                    if px > 0 and px < width:
                        n += 1
                        tot += elevation[py][px]
        return tot / n

    for i in range(steps):
        _antialias_step()


def rescale_value(original, prev_min, prev_max, min, max):
    """Rescale a given value.
    Given the value, the current min and max and the new min and max
    produce the rescaled value
    """
    f = float(original - prev_min) / (prev_max - prev_min)
    return min + ((max - min) * f)
