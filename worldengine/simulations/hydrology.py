from worldengine.simulations.basic import find_threshold_f
import numpy
    
#def droplet(elevation, pos, q, _watermap):
    ##what does this even do?
    #if q < 0:
        #return
    #x, y = pos
    #pos_elev = elevation[y, x] + _watermap[y, x]
    #lowers = []
    #min_higher = None
    #min_lower = None
    ## pos_min_higher = None  # TODO: no longer used?
    #tot_lowers = 0
    #for p in world.tiles_around((x, y)):#TODO: switch to numpy
        #px, py = p
        #e = elevation[py, px] + _watermap[py, px]
        #if e < pos_elev:
            #dq = int(pos_elev - e) << 2
            #if min_lower is None or e < min_lower:
                #min_lower = e
                #if dq == 0:
                    #dq = 1
            #lowers.append((dq, p))
            #tot_lowers += dq

        #else:
            #if min_higher is None or e > min_higher:
                #min_higher = e
                ## pos_min_higher = p
    #if lowers:
        #f = q / tot_lowers
        #for l in lowers:
            #s, p = l
            #if not world.is_ocean(p):
                #px, py = p
                #ql = f * s
                ## ql = q
                #going = ql > 0.05
                #_watermap[py, px] += ql
                #if going:
                    #droplet(world, p, ql, _watermap)
    #else:
        #_watermap[y, x] += q

#ocean = world.layers['ocean'].data
def watermap_sim(elevation,precipitation,ocean, n=20000):
    
    height,width=ocean.shape
    
    _watermap_data = numpy.zeros((height, width), dtype=float)

    # This indirectly calls the global rng.
    # We want different implementations of _watermap 
    # and internally called functions (especially random_land)
    # to show the same rng behaviour and not contamine the state of the global rng
    # should anyone else happen to rely on it.
    
    #if False:
        
        ##not sure I understood how this works
        ##especially not sure why it needs a random land sample?
        
        #land_sample = world.random_land(n)

        #if land_sample[0] is not None:
            #for i in range(n):
                #x, y = land_sample[2*i], land_sample[2*i+1]
                #if precipitation[y][x] > 0:
                    #droplet(elevation, (x, y), precipitation[y][x], _watermap_data)

    
    thresholds = dict()
    thresholds['creek'] = find_threshold_f(_watermap_data, 0.05, ocean=ocean)
    thresholds['river'] = find_threshold_f(_watermap_data, 0.02, ocean=ocean)
    thresholds['main river'] = find_threshold_f(_watermap_data, 0.007, ocean=ocean)
        
    return _watermap_data, thresholds
