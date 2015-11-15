""" This program generates some of the data used by tests other data samples could have been
obtained simply by running the program.

The data lives in the worldengine-data repo: https://github.com/Mindwerks/worldengine-data

Note that we want to have common data in tests, instead of generating them on the fly
because the plate simulation steps do not provide the same results on all the platforms
"""

import os
import numpy
from worldengine.plates import world_gen, _plates_simulation


def main(tests_data_dir):
    numpy.random.seed(28070)
    w = world_gen("seed_28070", 300, 200, 28070)
    w.protobuf_to_file("%s/seed_28070.world" % tests_data_dir)


if __name__ == '__main__':
    blessed_images_dir = os.path.dirname(os.path.realpath(__file__))
    tests_data_dir = os.path.abspath(os.path.join(blessed_images_dir, '../data'))
    main(tests_data_dir)
