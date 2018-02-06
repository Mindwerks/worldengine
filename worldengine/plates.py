# Every reference to platec has to be kept separated because it is a C
# extension which is not available when using this project from jython

import platec
import time

def filter_plates_args(all_dict):
    l=["seed", "width", "height", "sea_level","erosion_period",
     "folding_ratio","aggr_overlap_abs","aggr_overlap_rel",
     "cycle_count","number_of_plates"]
    plates_kwargs={}
    for key in l:
        if key in all_dict:
            plates_kwargs[key]=all_dict[key]
    return plates_kwargs


def generate_plates_simulation(seed, 
                                width=512, 
                                height=512, 
                                sea_level=0.65,
                               erosion_period=60, 
                               folding_ratio=0.02,
                               aggr_overlap_abs=1000000, 
                               aggr_overlap_rel=0.33,
                               cycle_count=2, 
                               number_of_plates=10,
                               verbose=False):
                                   
    num_plates=number_of_plates

    if verbose:
        start_time = time.time()
        
    p = platec.create(seed, width, height, sea_level, erosion_period,
                      folding_ratio, aggr_overlap_abs, aggr_overlap_rel,
                      cycle_count, num_plates)
    # Note: To rescale the worlds heightmap to roughly Earths scale, multiply by 2000.

    while platec.is_finished(p) == 0:
        # TODO: add a if verbose: message here?
        platec.step(p)
    hm = platec.get_heightmap(p)
    pm = platec.get_platesmap(p)
    if verbose:
        elapsed_time = time.time() - start_time
        print("...plates.generate_plates_simulation() complete. " +
              "Elapsed time " + str(elapsed_time) + " seconds.")
    return hm, pm
