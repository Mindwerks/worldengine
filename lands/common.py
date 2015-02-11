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


def scale(original_map, target_width, target_height):

    def _get_interleave_value(original_map, x, y):
        """x and y can be float value"""

        weight_next_x, base_x = math.modf(x)
        weight_preceding_x = 1.0 - weight_next_x
        weight_next_y, base_y = math.modf(y)
        weight_preceding_y = 1.0 - weight_next_y

        base_x = int(base_x)
        base_y = int(base_y)

        sum = 0.0

        # In case the point is right on the border, the weight
        # of the next point will be zero and we will not access
        # it
        combined_weight = weight_preceding_x * weight_preceding_y
        if combined_weight > 0.0:
            sum += combined_weight * original_map[base_y][base_x]

        combined_weight = weight_preceding_x * weight_next_y
        if combined_weight > 0.0:
            sum += combined_weight * original_map[base_y + 1][base_x]

        combined_weight = weight_next_x * weight_preceding_y
        if combined_weight > 0.0:
            sum += combined_weight * original_map[base_y][base_x + 1]

        combined_weight = weight_next_x * weight_next_y
        if combined_weight > 0.0:
            sum += combined_weight * original_map[base_y + 1][base_x + 1]

        return sum

    original_width = len(original_map[0])
    original_height = len(original_map)

    y_factor = float(original_height - 1) / (target_height - 1)
    x_factor = float(original_width - 1) / (target_width - 1)

    scaled_map = [[0 for x in range(target_width)] for y in range(target_height)]
    for scaled_y in range(target_height):
        original_y = y_factor * scaled_y
        for scaled_x in range(target_width):
            original_x = x_factor * scaled_x
            scaled_map[scaled_y][scaled_x] = _get_interleave_value(original_map, original_x, original_y)

    return scaled_map


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
    f = float(original - prev_min) / (prev_max - prev_min)
    return min + ((max - min) * f)
