from worldengine.simulations.basic import find_threshold_f


class HumiditySimulation(object):
    @staticmethod
    def is_applicable(world):
        return world.has_precipitations() and world.has_irrigation() and (
            not world.has_humidity())

    def execute(self, world, seed):
        assert seed
        world.humidity = self._calculate(world)

    @staticmethod
    def _calculate(world):
        humidity = dict()
        humidity['data'] = [[0 for x in xrange(world.width)] for y in
                            xrange(world.height)]  # TODO: replace with numpy

        for y in xrange(world.height):
            for x in xrange(world.width):
                humidity['data'][y][x] = world.precipitation['data'][y][x] + \
                    world.irrigation[y][x]

        # These were originally evenly spaced at 12.5% each but changing them
        # to a bell curve produced better results
        humidity['quantiles'] = {}
        humidity['quantiles']['12'] = find_threshold_f(humidity['data'], 0.02,
                                                       world.ocean)
        humidity['quantiles']['25'] = find_threshold_f(humidity['data'], 0.09,
                                                       world.ocean)
        humidity['quantiles']['37'] = find_threshold_f(humidity['data'], 0.26,
                                                       world.ocean)
        humidity['quantiles']['50'] = find_threshold_f(humidity['data'], 0.50,
                                                       world.ocean)
        humidity['quantiles']['62'] = find_threshold_f(humidity['data'], 0.74,
                                                       world.ocean)
        humidity['quantiles']['75'] = find_threshold_f(humidity['data'], 0.91,
                                                       world.ocean)
        humidity['quantiles']['87'] = find_threshold_f(humidity['data'], 0.98,
                                                       world.ocean)
        return humidity
