import numpy


class IcecapSimulation(object):
    # This class creates an "ice-map", i.e. a numpy array with positive values that describe the thickness of the ice at
    # a certain spot of the world.
    # Ice can appear wherever there is an ocean and the temperature is cold enough.

    # TODO: Find out if a desert planet could still freeze or if the freeze-threshold is dynamic.
    # TODO: Freeze rivers etc.

    @staticmethod
    def is_applicable(world):
        return world.has_ocean() and world.has_temperature()

    def execute(self, world, seed):
        world.set_icecap(self._calculate(world, seed))

    @staticmethod
    def _calculate(world, seed):
        # Notes on performance:
        #  -method is run once per generation
        #  -iterations        : width * height
        #  -memory consumption: width * height * sizeof(numpy.float) (permanent)
        #                       width * height * sizeof(numpy.bool) (temporary)

        # constants for convenience (or performance)
        ocean = world.layers['ocean'].data
        temperature = world.layers['temperature'].data

        # primary constants (could be used as global variables at some point); all values should be in [0, 1]
        max_freeze_percentage = 0.60  # only the coldest x% of the cold area will freeze (0 = no ice, 1 = all ice)
        freeze_chance_window = 0.20  # the warmest x% of freezable area won't completely freeze (RNG decides)
        surrounding_tile_influence = 0.5  # chance-modifier to freeze a slightly warm tile when neighbors are frozen

        # secondary constants
        temp_min = temperature.min()  # coldest spot in the world
        freeze_threshold = world.layers['temperature'].thresholds[0][1]  # upper temperature-limit for freezing effects
        # Cold biomes: TODO: find and pick most appropriate threshold
        #    polar: self.temperature['thresholds'][0][1]
        #   alpine: self.temperature['thresholds'][1][1]
        #   boreal: self.temperature['thresholds'][2][1]

        # derived constants
        freeze_threshold = (freeze_threshold - temp_min) * max_freeze_percentage  # calculate freeze threshold above min
        freeze_chance_threshold = freeze_threshold * (1.0 - freeze_chance_window)

        # local variables
        icecap = numpy.zeros((world.height, world.width), dtype=float)
        rng = numpy.random.RandomState(seed)  # create our own random generator

        # map that is True whenever there is land or (certain) ice around
        solid_map = numpy.logical_or(temperature <= freeze_chance_threshold + temp_min, numpy.logical_not(ocean))

        for y in range(world.height):
            for x in range(world.width):
                if world.is_ocean((x, y)):  # or world.river_map[y, x] > 0 or world.lake_map[y, x] > 0 or world.watermap['data'][y, x] > 0:
                    t = temperature[y, x]
                    if t - temp_min < freeze_threshold:
                        # map temperature to freeze-chance (linear interpolation)
                        chance = numpy.interp(t, [temp_min, freeze_chance_threshold, freeze_threshold], [1.0, 1.0, 0.0])
                        # *will* freeze for temp_min <= t <= freeze_chance_threshold
                        # *can* freeze for freeze_chance_threshold < t < freeze_threshold

                        # count number of frozen/solid tiles around this one
                        if 0 < x < world.width - 1 and 0 < y < world.height - 1:  # exclude borders
                            surr_tiles = solid_map[y-1:y+2, x-1:x+2]
                            chance_mod = numpy.count_nonzero(surr_tiles)
                            chance_mod -= 1 if solid_map[y, x] else 0  # remove center-tile (i.e. the current tile)

                            # map amount of tiles to chance-modifier, [-1.0, 1.0]
                            chance_mod = numpy.interp(chance_mod, [0, surr_tiles.size - 1], [-1.0, 1.0])
                            chance += chance_mod * surrounding_tile_influence

                        if rng.rand() <= chance:  # always freeze for chance >= 1.0, never for <= 0.0
                            solid_map[y, x] = True  # mark tile as frozen
                            icecap[y, x] = freeze_threshold - (t - temp_min)  # thickness of the ice (arbitrary scale)

        return icecap
