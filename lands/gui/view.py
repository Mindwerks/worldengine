__author__ = 'Federico Tomassetti'

from PyQt4 import QtGui
from lands.draw import elevation_color
import lands.drawing_functions

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


def cos(x):
    import math
    return math.cos(x/180 * 3.14)


def hsi_to_rgb(hue, saturation, intensity):
    h = H = hue % 360
    S = saturation
    I = intensity
    IS = saturation * intensity

    if h==0:
        R = I + 2 * IS
        G = I - IS
        B = I - IS
    elif 0 < H and H < 120:
        R = I + IS*cos(H)/cos(60-H)
        G = I + IS*(1 - cos(H)/cos(60-H))
        B = I - IS
    elif H == 120:
        R = I - IS
        G = I + 2 * IS
        B = I - IS
    elif 120 < H and H < 240:
        R = I - IS
        G = I + ((IS*cos(H-120))/cos(180-H))
        B = I + IS*(1 - cos(H-120)/cos(180-H))
    elif H == 240:
        R = I - IS
        G = I - IS
        B = I + 2 * IS
    elif 240 < H and H < 360:
        R = I + IS*(1 - cos(H-240)/cos(300-H))
        G = I - IS
        B = I + IS*cos(H-240)/cos(300-H)
    else:
        raise "Unexpected"
    return (int(R), int(G), int(B))


def draw_plates_on_screen(world, canvas):
    width = world.width
    height = world.height
    n_plates = world.n_actual_plates()
    for y in range(0, height):
        for x in range(0, width):
            h = world.plates[y][x]*(360/n_plates)
            s = 0.5
            i = 64.0
            r, g, b = hsi_to_rgb(h, s, i)
            col = QtGui.QColor(r, g, b)
            canvas.setPixel(x, y, col.rgb())


def draw_plates_and_elevation_on_screen(world, canvas):
    width = world.width
    height = world.height
    n_plates = world.n_actual_plates()
    max_el = world.max_elevation()
    min_el = world.min_elevation()
    delta_el = max_el - min_el
    for y in range(0, height):
        for x in range(0, width):
            h = world.plates[y][x]*(360/n_plates)
            el = world.elevation['data'][y][x]
            s = 0.6
            i = 40.0 + 60.0 * ((el-min_el)/delta_el)
            r, g, b = hsi_to_rgb(h, s, i)
            col = QtGui.QColor(r, g, b)
            canvas.setPixel(x, y, col.rgb())


def draw_land_on_screen(world, canvas):
    width = world.width
    height = world.height
    land_color = QtGui.QColor(0, 200, 0).rgb()
    ocean_color = QtGui.QColor(0, 0, 200).rgb()
    for y in range(0, height):
        for x in range(0, width):
            if world.is_land((x,y)):
                canvas.setPixel(x, y, land_color)
            else:
                canvas.setPixel(x, y, ocean_color)


def draw_ancientmap_on_screen(world, canvas):
    drawing_functions.draw_oldmap_on_pixels(world, pixels)
