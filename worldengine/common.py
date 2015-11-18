import sys
import copy
import numpy #for the _equal method only

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


def anti_alias(map, steps):#TODO: There is probably a bit of numpy-optimization that can be done here.
    """
    Execute the anti_alias operation steps times on the given map
    """
    height, width = map.shape

    def _anti_alias_step(original):
        anti_aliased = copy.deepcopy(original)
        for y in range(height):
            for x in range(width):
                anti_aliased[y, x] = anti_alias_point(original, x, y)
        return anti_aliased

    def anti_alias_point(original, x, y):
        n = 2
        tot = map[y, x] * 2
        for dy in range(-1, +2):
            py = (y + dy) % height
            for dx in range(-1, +2):
                px = (x + dx) % width
                n += 1
                tot += original[py, px]
        return tot / n

    current = map
    for i in range(steps):
        current = _anti_alias_step(current)
    return current


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
        return(a == b)
