import numpy

from worldengine.simplex import snoise2
from worldengine.simulations.basic import find_threshold_f


class TemperatureSimulation:
    @staticmethod
    def is_applicable(world):
        return not world.has_temperature()

    def execute(self, world, seed):
        e = world.layers["elevation"].data
        ml = world.start_mountain_th()  # returns how many percent of the world are mountains
        ocean = world.layers["ocean"].data

        t = self._calculate(world, seed, e, ml)
        t_th = [
            ("polar", find_threshold_f(t, world.temps[0], ocean)),
            ("alpine", find_threshold_f(t, world.temps[1], ocean)),
            ("boreal", find_threshold_f(t, world.temps[2], ocean)),
            ("cool", find_threshold_f(t, world.temps[3], ocean)),
            ("warm", find_threshold_f(t, world.temps[4], ocean)),
            ("subtropical", find_threshold_f(t, world.temps[5], ocean)),
            ("tropical", None),
        ]
        world.temperature = (t, t_th)

    @staticmethod
    def _calculate(world, seed, elevation, mountain_level):
        width = world.width
        height = world.height

        rng = numpy.random.RandomState(seed)  # create our own random generator
        base = rng.randint(0, 4096)

        """
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
        """
        distance_to_sun_hwhm = 0.12
        axial_tilt_hwhm = 0.07

        # derive parameters
        distance_to_sun = rng.normal(loc=1.0, scale=distance_to_sun_hwhm / 1.177410023)
        distance_to_sun = max(0.1, distance_to_sun)  # clamp value; no planets inside the star allowed
        distance_to_sun *= distance_to_sun  # prepare for later usage; use inverse-square law
        # TODO: an atmosphere would soften the effect of distance_to_sun by *some* factor
        axial_tilt = rng.normal(scale=axial_tilt_hwhm / 1.177410023)
        axial_tilt = min(max(-0.5, axial_tilt), 0.5)  # cut off Gaussian

        border = width / 4
        octaves = 8  # number of passes of snoise2
        freq = 16.0 * octaves
        n_scale = 1024 / float(height)

        x = numpy.arange(width)
        y = numpy.arange(height).reshape(-1, 1)
        y_scaled = y / height - 0.5  # -0.5...0.5

        # map/linearly interpolate y_scaled to latitude measured from where the most sunlight hits the world:
        # 1.0 = hottest zone, 0.0 = coldest zone
        latitude_factor = numpy.interp(
            y_scaled, [axial_tilt - 0.5, axial_tilt, axial_tilt + 0.5], [0.0, 1.0, 0.0], left=0.0, right=0.0
        )

        y_sampled = (y * n_scale) / freq
        n = snoise2((x * n_scale) / freq, y_sampled, octaves, base=base).astype(float)

        # Added to allow noise pattern to wrap around right and left.
        wrapped = snoise2(((x * n_scale) + width) / freq, y_sampled, octaves, base=base).astype(float)
        n = numpy.where(x <= border, n * x / border + wrapped * (border - x) / border, n)

        temp = (latitude_factor * 12 + n * 1) / 13.0 / distance_to_sun

        # vary temperature based on height
        drop = (elevation.astype(float) - mountain_level) / 30
        altitude_factor = numpy.where(elevation > (mountain_level + 29), 0.033, 1.00 - drop)
        return numpy.where(elevation > mountain_level, temp * altitude_factor, temp)
