import time
import numpy
from noise import snoise2

from worldengine.simulations.basic import find_threshold_f
from worldengine.common import get_verbose


class PrecipitationSimulation(object):

    @staticmethod
    def is_applicable(world):
        return not world.has_precipitations()

    def execute(self, world, seed):
        if get_verbose():
            start_time = time.time()
        pre_calculated = self._calculate(seed, world)
        ths = [
            ('low', find_threshold_f(pre_calculated, 0.75, world.ocean)),
            ('med', find_threshold_f(pre_calculated, 0.3, world.ocean)),
            ('hig', None)
        ]
        world.set_precipitation(pre_calculated, ths)
        if get_verbose():
            elapsed_time = time.time() - start_time
            print(
                "...precipitations calculated. Elapsed time %f  seconds."
                % elapsed_time)

    @staticmethod
    def _calculate(seed, world):
        """Precipitation is a value in [-1,1]"""
        rng = numpy.random.RandomState(seed)  # create our own random generator
        base = rng.randint(0, 4096)

        curve_gamma = world.gamma_curve
        curve_bonus = world.curve_offset
        height = world.height
        width = world.width
        border = width / 4
        precipitations = numpy.zeros((height, width), dtype=float)

        octaves = 6
        freq = 64.0 * octaves

        n_scale = 1024 / float(height) #This is a variable I am adding. It exists
                                       #so that worlds sharing a common seed but
                                       #different sizes will have similar patterns

        for y in range(height):#TODO: numpy
            for x in range(width):
                n = snoise2((x * n_scale) / freq, (y * n_scale) / freq, octaves, base=base)

                # Added to allow noise pattern to wrap around right and left.
                if x < border:
                    n = (snoise2( (x * n_scale) / freq, (y * n_scale) / freq, octaves,
                                 base=base) * x / border) + (
                        snoise2(( (x * n_scale) + width) / freq, (y * n_scale) / freq, octaves,
                                base=base) * (border - x) / border)

                precipitations[y, x] = n

        #find ranges
        min_precip = precipitations.min()
        max_precip = precipitations.max()
        min_temp = world.temperature['data'].min()
        max_temp = world.temperature['data'].max()
        precip_delta = (max_precip - min_precip)
        temp_delta = (max_temp - min_temp)
        
        #normalize temperature and precipitation arrays
        t = (world.temperature['data'] - min_temp) / temp_delta
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
        
        curve = (numpy.power(t, curve_gamma) * (1-curve_bonus)) + curve_bonus
        precipitations = numpy.multiply(p, curve)

        #Renormalize precipitation because the precipitation 
        #changes will probably not fully extend from -1 to 1.
        min_precip = precipitations.min()
        max_precip = precipitations.max()
        precip_delta = (max_precip - min_precip)
        precipitations = (((precipitations - min_precip) / precip_delta) * 2) - 1
        
        return precipitations
