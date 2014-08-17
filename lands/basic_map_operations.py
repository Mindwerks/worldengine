__author__ = 'Federico Tomassetti'

import math
import random


def random_point(width, height):
    return random.randrange(0, width), random.randrange(0, height)


def distance(pa, pb):
    ax, ay = pa
    bx, by = pb
    return math.sqrt((ax - bx) ** 2 + (ay - by) ** 2)


def distance3(pa, pb):
    ax, ay = pa
    bx, by = pb
    return (ax - bx) ** 3 + (ay - by) ** 3


def nearest(p, hot_points, distance_f=distance):
    min_dist = None
    nearest_hp_i = None
    for i, hp in enumerate(hot_points):
        dist = distance_f(p, hp)
        if (None == min_dist) or dist < min_dist:
            min_dist = dist
            nearest_hp_i = i
    return nearest_hp_i
