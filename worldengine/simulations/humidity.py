from worldengine.simulations.basic import find_threshold_f
import numpy


class HumiditySimulation(object):
    @staticmethod
    def is_applicable(world):
        return world.has_precipitations() and world.has_irrigation() and (
            not world.has_humidity())

    def execute(self, world, seed):
        assert seed is not None
        world.humidity = self._calculate(world)

    @staticmethod
    def _calculate(world):
        humidity = dict()
        temperatureWeight = 2.3
        precipitationWeight = 1.0
        irrigationWeight = 3
        humidity['data'] = numpy.zeros((world.height, world.width), dtype=float)

        humidity['data'] = (world.precipitation['data'] * precipitationWeight - world.irrigation * irrigationWeight)/(precipitationWeight + irrigationWeight)

        # These were originally evenly spaced at 12.5% each but changing them
        # to a bell curve produced better results
        humidity['quantiles'] = {}
        humidity['quantiles']['12'] = find_threshold_f(humidity['data'], 0.002,
                                                       world.ocean)
        humidity['quantiles']['25'] = find_threshold_f(humidity['data'], 0.014,
                                                       world.ocean)
        humidity['quantiles']['37'] = find_threshold_f(humidity['data'], 0.073,
                                                       world.ocean)
        humidity['quantiles']['50'] = find_threshold_f(humidity['data'], 0.236,
                                                       world.ocean)
        humidity['quantiles']['62'] = find_threshold_f(humidity['data'], 0.507,
                                                       world.ocean)
        humidity['quantiles']['75'] = find_threshold_f(humidity['data'], 0.778,
                                                       world.ocean)
        humidity['quantiles']['87'] = find_threshold_f(humidity['data'], 0.941,
                                                       world.ocean)
        return humidity
