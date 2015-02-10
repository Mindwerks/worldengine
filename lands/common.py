__author__ = 'Federico Tomassetti'

def get_verbose():
    global verbose
    if not 'verbose' in globals():
        return False
    else:
        return True

def set_verbose(value):
    global verbose
    verbose = value