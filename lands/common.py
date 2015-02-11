__author__ = 'Federico Tomassetti'

verbose = False


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


def is_pow_of_two(num):
    return ((num & (num - 1)) == 0) and num != 0


class Counter(object):

    def __init__(self):
        self.c = {}

    def count(self, what):
        if what not in self.c:
            self.c[what] = 0
        self.c[what] += 1

    def printself(self):
        for w in self.c.keys():
            print("%s : %i" % (w, self.c[w]))


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
