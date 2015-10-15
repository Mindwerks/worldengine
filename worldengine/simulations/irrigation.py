import numpy

class IrrigationSimulation(object):
    @staticmethod
    def is_applicable(world):
        return world.has_watermap() and (not world.has_irrigation())

    def execute(self, world, seed):
        world.irrigation = self._calculate(world)

    @staticmethod
    def _calculate(world):
        #Notes on performance:
        #  -method is run once per generation
        #  -iterations        : width * height * (2 * radius + 1)^2
        #  -memory consumption: width * height * 8 Byte (numpy 1.9.2)

        width = world.width
        height = world.height
        radius = 10

        #----------prepare helper arrays
        #create array of pre-calculated values -> less calls to sqrt(), square() and log()
        d = numpy.arange(-radius, radius + 1, 1, dtype=numpy.float)
        x, y = numpy.meshgrid(d, d)#x,y now contain x/y-coordinates of the distance-matrix
        
        #calculat the final matrix: ln(sqrt(x^2+y^2) + 1)
        logs = numpy.log1p(numpy.sqrt(numpy.add(numpy.square(x), numpy.square(y))))
        logs = numpy.add(logs, 1)
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
                        values[pt] += world.watermap['data'][y][x] / logs[it_logs.multi_index]

                    it_logs.iternext()
            it_all.iternext()

        return values
