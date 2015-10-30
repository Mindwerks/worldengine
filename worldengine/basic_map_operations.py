import math


def distance(pa, pb):
    ax, ay = pa
    bx, by = pb
    return math.sqrt((ax - bx) ** 2 + (ay - by) ** 2)


def index_of_nearest(p, hot_points, distance_f=distance):
    """Given a point and a set of hot points it found the hot point
    nearest to the given point. An arbitrary distance function can
    be specified
    :return the index of the nearest hot points, or None if the list of hot
            points is empty
    """
    min_dist = None
    nearest_hp_i = None
    for i, hp in enumerate(hot_points):
        dist = distance_f(p, hp)
        if min_dist is None or dist < min_dist:
            min_dist = dist
            nearest_hp_i = i
    return nearest_hp_i
