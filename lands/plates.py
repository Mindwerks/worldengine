__author__ = 'Federico Tomassetti'

# Every reference to platec has to be kept separated because it is a C extension
# which is not available when using this project from jython

from lands.geo import *
import platec


def array_to_matrix(array, width, height):
    if (len(array) != (width * height)):
        raise Exception("Array as not expected length")
    matrix = []
    for y in xrange(height):
        matrix.append([])
        for x in xrange(width):
            matrix[y].append(array[y * width + x])
    return matrix


def generate_plates_simulation(seed, width, height, sea_level=0.65, erosion_period=60,
                               folding_ratio=0.02, aggr_overlap_abs=1000000, aggr_overlap_rel=0.33,
                               cycle_count=2, num_plates=10):

    p = platec.create(seed, width, height, sea_level, erosion_period, folding_ratio,
                      aggr_overlap_abs, aggr_overlap_rel, cycle_count, num_plates)

    while platec.is_finished(p) == 0:
        platec.step(p)
    hm = platec.get_heightmap(p)
    pm = platec.get_platesmap(p)
    return hm, pm


def world_gen(name, seed, verbose, width, height, step="full", num_plates=10):
    e_as_array, p_as_array = generate_plates_simulation(seed, width, height, num_plates=num_plates)

    world = World(name, width, height)
    world.set_elevation(array_to_matrix(e_as_array, width, height), None)
    world.set_plates(array_to_matrix(p_as_array, width, height))

    center_land(world)
    if verbose:
        print("...plates simulated")
    elevnoise_on_world(world, random.randint(0, 4096))
    place_oceans_at_map_borders_on_world(world)
    initialize_ocean_and_thresholds(world)
    if verbose:
        print("...elevation noise added")

    return world_gen_from_elevation(world, name, seed, ocean_level=1.0, verbose=verbose, width=width, height=height,
                                    step=step)
