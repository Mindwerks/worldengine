import numpy
#import math


class IrrigationSimulation(object):
    @staticmethod
    def is_applicable(world):
        return world.has_watermap() and (not world.has_irrigation())

    def execute(self, world, seed):
        world.irrigation = self._calculate(world)

    @staticmethod
    def _calculate(world):
        width = world.width
        height = world.height
        radius = 10

        #----------prepare helper arrays
        #create array of distances so that less calls to sqrt() and square() occur
        logs = numpy.empty((2*radius + 1, 2*radius + 1), dtype=numpy.float)

        it_logs = numpy.nditer(logs, flags=['multi_index'], op_flags=['writeonly'])
        while not it_logs.finished:
            #shift the "center" of the array to (radius, radius)
            coordinate = (it_logs.multi_index[0] - radius, it_logs.multi_index[1] - radius)
            #store squared distance to the center
            it_logs[0] = numpy.square(coordinate[0]) + numpy.square(coordinate[1])
            it_logs.iternext()
        logs = numpy.sqrt(logs)

        #save time calculating log10()
        it_logs = numpy.nditer(logs, flags=['multi_index'], op_flags=['readwrite'])
        while not it_logs.finished:
            #store log10-calculation
            it_logs[0] = numpy.log10(it_logs[0] + 1) + 1
            it_logs.iternext()
        #----------preparations done

        #create output array
        values = numpy.zeros((width, height), dtype=numpy.float)

        it_all = numpy.nditer(values, flags=['multi_index'], op_flags=['readonly'])
        it_logs = numpy.nditer(logs, flags=['multi_index'], op_flags=['readonly'])
        while not it_all.finished:
            if world.is_land(it_all.multi_index):
                #iterate over area [[x-radius, x+radius], [y-radius, y+radius]]
                it_logs.reset()
                while not it_logs.finished:
                    #calculate absolute coordinates
                    coordinate = (it_all.multi_index[0] + it_logs.multi_index[0] - radius,
                                  it_all.multi_index[1] + it_logs.multi_index[1] - radius)

                    if coordinate >= (0, 0) and coordinate <= (width, height):
                        values[coordinate] += world.watermap['data'][it_all.multi_index[1]][it_all.multi_index[0]] / logs[it_logs.multi_index]

                    it_logs.iternext()
            it_all.iternext()

        values.transpose()

#        values = [[0 for x in range(width)] for y in range(height)]  # TODO: replace with numpy
#
#        for y in range(height):
#            for x in range(width):
#                if world.is_land((x, y)):
#                    for dy in range(-radius, radius + 1):   # TODO: below can be simplified
#                        if (y + dy) >= 0 and (y + dy) < world.height:
#                            for dx in range(-radius, radius + 1):
#                                if (x + dx) >= 0 and (x + dx) < world.width:
#                                    dist = math.sqrt(dx ** 2 + dy ** 2)
#                                    values[y + dy][x + dx] += \
#                                        world.watermap['data'][y][x] / (
#                                            math.log(dist + 1) + 1)

        return values