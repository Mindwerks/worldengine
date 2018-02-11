from noise import snoise2  # http://nullege.com/codes/search/noise.snoise2
import numpy

def planetary_parameters(rng,distance_to_sun=0.12,axial_tilt=0.07):
    
    '''
    Set up variables to take care of some orbital parameters:
     distance_to_sun: -Earth-like planet = 1.0
                      -valid range between ~0.7 and ~1.3
                            see https://en.wikipedia.org/wiki/Circumstellar_habitable_zone
                      -random value chosen via Gaussian distribution
                            see https://en.wikipedia.org/wiki/Gaussian_function
                      -width of distribution around 1.0 is determined by HWHM (half width at half maximum)
                      -HWHM is used to calculate the second parameter passed to random.gauss():
                            sigma = HWHM / sqrt(2*ln(2))
                      -*only HWHM* should be considered a parameter here
                      -most likely outcomes can be estimated:
                            HWHM * sqrt(2*ln(10)) / sqrt(2*ln(2)) = HWHM * 1.822615728;
                            e.g. for HWHM = 0.12: 0.78 < distance_to_sun < 1.22
     axial_tilt:      -the world/planet may move around its star at an angle
                            see https://en.wikipedia.org/wiki/Axial_tilt
                      -a value of 0.5 here would refer to an angle of 90 degrees, Uranus-style
                            see https://en.wikipedia.org/wiki/Uranus
                      -this value should usually be in the range -0.15 < axial_tilt < 0.15 for a habitable planet
    '''
    
    distance_to_sun_hwhm = distance_to_sun
    axial_tilt_hwhm = axial_tilt

    #derive parameters
    distance_to_sun = rng.normal(loc=1.0, scale=distance_to_sun_hwhm / 1.177410023)
    distance_to_sun = max(0.1, distance_to_sun)  # clamp value; no planets inside the star allowed
    distance_to_sun *= distance_to_sun  # prepare for later usage; use inverse-square law
    # TODO: an atmoshphere would soften the effect of distance_to_sun by *some* factor
    axial_tilt = rng.normal(scale=axial_tilt_hwhm / 1.177410023)
    axial_tilt = min(max(-0.5, axial_tilt), 0.5)  # cut off Gaussian
    #print("distance to sun",distance_to_sun)
    return distance_to_sun,axial_tilt
    
def temp_noise(x,y,n_scale,freq,octaves,base,border,width):

    #--v erm, this is just another stupid noise function?
    #don't we have one of those?
    n = snoise2((x * n_scale) / freq, (y * n_scale) / freq, octaves, base=base)

    # Added to allow noise pattern to wrap around right and left.
    if x <= border:
        n = (snoise2((x * n_scale) / freq, (y * n_scale) / freq, octaves,
                     base=base) * x / border) \
            + (snoise2(((x * n_scale) + width) / freq, (y * n_scale) / freq, octaves,
                       base=base) * (border - x) / border)
    return n

def single_temp(x,y,n,elevation,mountain_level,latitude_factor,distance_to_sun):
    
    t = (latitude_factor * 12 + n * 1) / 13.0 / distance_to_sun
    
    if elevation[y, x] > mountain_level:  # vary temperature based on height
        if elevation[y, x] > (mountain_level + 29):
            altitude_factor = 0.033
        else:
            altitude_factor = 1.00 - (
                float(elevation[y, x] - mountain_level) / 30)
        t *= altitude_factor
        
    return t

def temper_sim(elevation,ocean,mountain_level,wtemps=[0.874, 0.765, 0.594, 0.439, 0.366, 0.124],seed=1): 
    height,width=ocean.shape
    
    rng = numpy.random.RandomState(seed)  # create our own random generator
    
    base = rng.randint(0, 4096)
    temp = numpy.zeros((height, width), dtype=float)

    distance_to_sun,axial_tilt=planetary_parameters(rng)
    
    border = width / 4
    octaves = 8  # number of passes of snoise2
    freq = 16.0 * octaves
    n_scale = 1024 / float(height)

    for y in range(0, height):  
        # TODO: Check for possible numpy optimizations.
        y_scaled = float(y) / height - 0.5 

        #map/linearly interpolate y_scaled to latitude measured from where the most sunlight hits the world:
        #1.0 = hottest zone, 0.0 = coldest zone
        
        axial_vector =[axial_tilt - 0.5, axial_tilt, axial_tilt + 0.5]
        
        latitude_factor = numpy.interp(y_scaled, axial_vector,[0.0, 1.0, 0.0], left=0.0, right=0.0)
        for x in range(0, width):
            
            n=temp_noise(x,y,n_scale,freq,octaves,base,border,width)
            t=single_temp(x,y,n,elevation,mountain_level,latitude_factor,distance_to_sun)
            
            temp[y, x] = t
    
    #this is biome stuff, actually. what is this doing here.
    #the thresholds normalize the whole thing...
    
    t=temp
    t_th = [
        ('polar', wtemps[5]),#find_threshold_f(t, wtemps[0], ocean)),
        ('alpine', wtemps[4]),#find_threshold_f(t, wtemps[1], ocean)),
        ('boreal', wtemps[3]),#find_threshold_f(t, wtemps[2], ocean)),
        ('cool', wtemps[2]),#find_threshold_f(t, wtemps[3], ocean)),
        ('warm', wtemps[1]),#find_threshold_f(t, wtemps[4], ocean)),
        ('subtropical', wtemps[0]),#find_threshold_f(t, wtemps[5], ocean)),
        ('tropical', None)
    ]
    
    
    return temp,t_th
