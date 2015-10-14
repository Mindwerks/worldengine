import numpy

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
        #create array of pre-calculated values -> less calls to sqrt(), square() and log()
        logs = numpy.empty((2*radius + 1, 2*radius + 1), dtype=numpy.float)

        it_logs = numpy.nditer(logs, flags=['multi_index'], op_flags=['writeonly'])
        while not it_logs.finished:
            #shift the "center" of the array to (radius, radius)
            pt = (it_logs.multi_index[0] - radius, it_logs.multi_index[1] - radius)
            #store squared distance to the center
            sqrt = numpy.sqrt(numpy.square(pt[0]) + numpy.square(pt[1]))
            it_logs[0] = numpy.log1p(sqrt) + 1#equal to: ln(sqrt + 1) + 1
            it_logs.iternext()
        #----------preparations done

        #create output array
        values = numpy.zeros((height, width), dtype=numpy.float)

        it_all = numpy.nditer(values, flags=['multi_index'], op_flags=['readonly'])
        it_logs = numpy.nditer(logs, flags=['multi_index'], op_flags=['readonly'])
        while not it_all.finished:
            x = it_all.multi_index[1]
            y = it_all.multi_index[0]
            if world.is_land((x, y)):
                #iterate over area [[x-radius, x+radius], [y-radius, y+radius]]
                it_logs.reset()
                while not it_logs.finished:
                    #calculate absolute pts; (y, x)
                    pt = (y + it_logs.multi_index[0] - radius,
                                  x + it_logs.multi_index[1] - radius)

                    if 0 <= pt[0] < height and 0 <= pt[1] < width:
                        values[pt] += world.watermap['data'][y][x] /logs[it_logs.multi_index]

                    it_logs.iternext()
            it_all.iternext()

        return values