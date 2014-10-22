__author__ = 'Federico Tomassetti'

# Every reference to platec has to be kept separated because it is a C extension
# which is not available when using this project from jython

from geo import *
import platec

def generate_plates_simulation(seed, width, height, sea_level=0.65, erosion_period=60,
                               folding_ratio=0.02, aggr_overlap_abs=1000000, aggr_overlap_rel=0.33,
                               cycle_count=2, num_plates=10):
    # we use always the same values for plates simulation and we scale later
    map_side = 2048 #Increased to produce more detailed maps. pyplatecmodule.c also has to be updated.
    p = platec.create(seed, map_side, sea_level, erosion_period, folding_ratio,
                      aggr_overlap_abs, aggr_overlap_rel, cycle_count, num_plates)

    while platec.is_finished(p) == 0:
        platec.step(p)
    hm = platec.get_heightmap(p)

    hm = scale_map_in_array(hm, map_side, map_side, width, height)

    return hm

def world_gen(name, seed, verbose, width, height, step="full"):
    e_as_array = generate_plates_simulation(seed, width, height)
    e_as_array = center_elevation_map(e_as_array, width, height)
    if verbose:
        print("...plates simulated")
    e = [[e_as_array[y * width + x] for x in xrange(width)] for y in xrange(height)]
    elevnoise(e, random.randint(0, 4096))
    place_oceans_at_map_borders(e)
    if verbose:
        print("...elevation noise added")

    return world_gen_from_elevation(name, e, seed, ocean_level=1.0, verbose=verbose, width=width, height=height,
                                    step=step)
