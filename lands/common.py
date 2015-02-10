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
