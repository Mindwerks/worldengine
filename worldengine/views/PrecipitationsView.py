from worldengine.views.basic import color_prop
from PyQt4 import QtGui


class PrecipitationsView(object):

    @staticmethod
    def is_applicable(world):
        return world.has_precipitations()

    @staticmethod
    def draw(world, canvas):
        width = world.width
        height = world.height
        low_th = world.precipitation['thresholds'][0][1]
        med_th = world.precipitation['thresholds'][1][1] - 0.10
        hig_th = med_th + 0.25
        color1 = (0, 47, 255)
        color2 = (0, 255, 255)
        color3 = (0, 255, 0)
        color4 = (255, 85, 0)
        color5 = (255, 0, 0)
        for y in range(0, height):
            for x in range(0, width):
                p = world.precipitation['data'][y][x]
                if world.is_ocean((x, y)):
                    r = g = b = 255
                elif p < low_th:
                    r, g, b = color_prop(color1, color2, -1.0, low_th, p)
                elif p < med_th:
                    r, g, b = color_prop(color2, color3, low_th, med_th, p)
                elif p < hig_th:
                    r, g, b = color_prop(color3, color4, med_th, hig_th, p)
                else:
                    r, g, b = color_prop(color4, color5, hig_th, 1.0, p)
                col = QtGui.QColor(r, g, b)
                canvas.setPixel(x, y, col.rgb())
