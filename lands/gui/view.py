__author__ = 'Federico Tomassetti'

from PyQt4 import QtGui
from draw import elevation_color

def draw_simple_elevation_on_screen(world, canvas):
    width = world.width
    height = world.height
    for y in range(0, height):
        for x in range(0, width):
            e = world.elevation['data'][y][x]
            r, g, b = elevation_color(e)
            col = QtGui.QColor(int(r*255),int(g*255),int(b*255))
            canvas.setPixel(x, y, col.rgb())

def draw_bw_elevation_on_screen(world, canvas):
    width = world.width
    height = world.height
    max_el = world.max_elevation()
    min_el = world.min_elevation()
    delta_el = max_el - min_el
    for y in range(0, height):
        for x in range(0, width):
            e = world.elevation['data'][y][x]
            e_normalized = (e - min_el) / delta_el
            r = g = b = e_normalized
            col = QtGui.QColor(int(r*255),int(g*255),int(b*255))
            canvas.setPixel(x, y, col.rgb())
