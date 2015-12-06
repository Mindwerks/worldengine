import numpy
from noise import snoise2

class WindSimulation(object):

    @staticmethod
    def is_applicable(world):
        return not world.has_wind()

    def execute(self, world, seed):
        assert seed is not None
        direction = self._calculate(world, 0.5, seed)
        world.set_wind_direction(direction)

    @staticmethod
    def _calculate(world, distorsion_factor, seed):
        NORTH = 0.0
        EAST = 0.25
        SOUTH = 0.5
        WEST = 0.75

        def _set_line_to_gradient(data, y, start_y, end_y, start_value, end_value):
            delta = float(end_y - start_y)
            start_affinity = float(end_y - y) / delta
            end_affinity = 1.0 - start_affinity
            value = start_value * start_affinity + end_value * end_affinity
            data[y] = value

        def _wrap(value):
            while value < 0.0:
                value += 1.0
            while value > 1.0:
                value -= 1.0
            return value

        # This is based on the algorithm described here: http://www.dungeonleague.com/2010/03/28/wind-direction/
        # We initially have a direction which depends only on the latitude:
        #
        # North Pole = South
        # North Circle = North
        # North Tropic = East
        # Equator = West
        # South Tropic = East
        # South Circle = South
        # South Pole = North
        #
        # Then we add noise to that

        NORTH_POLE = int(world.height * 0.0)
        NORTH_CIRCLE = int(world.height * 0.16)
        NORTH_TROPIC = int(world.height * 0.34)
        EQUATOR = int(world.height * 0.5)
        SOUTH_TROPIC = int(world.height * 0.66)
        SOUTH_CIRCLE = int(world.height * 0.84)
        SOUTH_POLE = int(world.height * 1.0)

        data = numpy.zeros((world.height, world.width), dtype=float)
        for y in range(NORTH_POLE, NORTH_CIRCLE):
            _set_line_to_gradient(data, y, NORTH_POLE, NORTH_CIRCLE, SOUTH, NORTH)
        for y in range(NORTH_CIRCLE, NORTH_TROPIC):
            _set_line_to_gradient(data, y, NORTH_CIRCLE, NORTH_TROPIC, NORTH, EAST)
        for y in range(NORTH_TROPIC, EQUATOR):
            _set_line_to_gradient(data, y, NORTH_TROPIC, EQUATOR, EAST, WEST)
        for y in range(EQUATOR, SOUTH_TROPIC):
            _set_line_to_gradient(data, y, EQUATOR, SOUTH_TROPIC, WEST, EAST)
        for y in range(SOUTH_TROPIC, SOUTH_CIRCLE):
            _set_line_to_gradient(data, y, SOUTH_TROPIC, SOUTH_CIRCLE, EAST, SOUTH)
        for y in range(SOUTH_CIRCLE, SOUTH_POLE):
            _set_line_to_gradient(data, y, SOUTH_CIRCLE, SOUTH_POLE, SOUTH, NORTH + 1.0)

        #
        # Generate noise
        #

        rng = numpy.random.RandomState(seed)  # create our own random generator
        base = rng.randint(0, 4096)

        height = world.height
        width = world.width
        border = width / 4

        octaves = 6
        freq = 64.0 * octaves

        n_scale = 1024 / float(height) #This is a variable I am adding. It exists
                                       #so that worlds sharing a common seed but
                                       #different sizes will have similar patterns

        for y in range(height): #TODO: numpy
            for x in range(width):
                n = snoise2((x * n_scale) / freq, (y * n_scale) / freq, octaves, base=base)

                # Added to allow noise pattern to wrap around right and left.
                if x < border:
                    n = (snoise2((x * n_scale) / freq, (y * n_scale) / freq, octaves, base=base) * x / border) + \
                        (snoise2(((x * n_scale) + width) / freq, (y * n_scale) / freq, octaves, base=base) * \
                        (border - x) / border)

                data[y, x] = _wrap(data[y, x] + n * distorsion_factor)

        return data
