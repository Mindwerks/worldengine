from PyQt4 import QtGui


class WatermapView(object):

    @staticmethod
    def is_applicable(world):
        return world.has_watermap()

    @staticmethod
    def draw(world, canvas):
        width = world.width
        height = world.height
        th = world.watermap['thresholds']['river']
        for y in range(0, height):
            for x in range(0, width):
                if world.is_ocean((x, y)):
                    r = g = 0
                    b = 255
                else:
                    w = world.watermap['data'][y][x]
                    if w > th:
                        r = g = 0
                        b = 255
                    else:
                        r = g = b = 0
                col = QtGui.QColor(r, g, b)
                canvas.setPixel(x, y, col.rgb())
