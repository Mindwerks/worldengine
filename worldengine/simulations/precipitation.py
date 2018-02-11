import numpy
from worldengine.simulations.basic import find_threshold_f, base_noise_map
    
def precipitation_sim(ocean,norm_t,seed,curve_gamma,curve_bonus):
    """Precipitation is a value in [-1,1]"""
    
    shape = ocean.shape
        
    precipitations=base_noise_map(shape,seed)
           
    #find ranges
    min_precip = precipitations.min()
    max_precip = precipitations.max()
    
    precip_delta = (max_precip - min_precip)
    
    #normalize temperature and precipitation arrays
    
    p = (precipitations - min_precip) / precip_delta
    
    #modify precipitation based on temperature
    
    #--------------------------------------------------------------------------------
    #
    # Ok, some explanation here because why the formula is doing this may be a
    # little confusing. We are going to generate a modified gamma curve based on 
    # normalized temperature and multiply our precipitation amounts by it.
    #
    # numpy.power(t,curve_gamma) generates a standard gamma curve. However
    # we probably don't want to be multiplying precipitation by 0 at the far
    # side of the curve. To avoid this we multiply the curve by (1 - curve_bonus)
    # and then add back curve_bonus. Thus, if we have a curve bonus of .2 then
    # the range of our modified gamma curve goes from 0-1 to 0-.8 after we
    # multiply and then to .2-1 after we add back the curve_bonus.
    #
    # Because we renormalize there is not much point to offsetting the opposite end
    # of the curve so it is less than or more than 1. We are trying to avoid
    # setting the start of the curve to 0 because f(t) * p would equal 0 when t equals
    # 0. However f(t) * p does not automatically equal 1 when t equals 1 and if we
    # raise or lower the value for f(t) at 1 it would have negligible impact after
    # renormalizing.
    #
    #--------------------------------------------------------------------------------
    
    
    curve = (numpy.power(norm_t, curve_gamma) * (1-curve_bonus)) + curve_bonus
    precipitations = numpy.multiply(p, curve)

    #Renormalize precipitation because the precipitation 
    #changes will probably not fully extend from -1 to 1.
    
    min_precip = precipitations.min()
    max_precip = precipitations.max()
    precip_delta = (max_precip - min_precip)
    precipitations = (((precipitations - min_precip) / precip_delta) * 2) - 1
    
    pre_calculated = precipitations  
    
    ths = [
        ('low', find_threshold_f(pre_calculated, 0.75, ocean)),
        ('med', find_threshold_f(pre_calculated, 0.3, ocean)),
        ('hig', None)
    ]
    
    return pre_calculated, ths
    
