__author__ = 'Federico Tomassetti'


def find_threshold(elevation, land_perc, ocean=None):
    width = len(elevation[0])
    height = len(elevation)

    def count(e):
        tot = 0
        for y in range(0, height):
            for x in range(0, width):
                if elevation[y][x] > e and (ocean is None or not ocean[y][x]):
                    tot += 1
        return tot

    def search(a, b, desired):
        if (not type(a) == int) or (not type(b) == int):
            raise "A and B should be int"
        if a == b:
            return a
        if (b - a) == 1:
            ca = count(a)
            cb = count(b)
            dista = abs(desired - ca)
            distb = abs(desired - cb)
            if dista < distb:
                return a
            else:
                return b
        m = int((a + b) / 2)
        cm = count(m)
        if desired < cm:
            return search(m, b, desired)
        else:
            return search(a, m, desired)

    all_land = width * height
    if ocean:
        for y in range(0, height):
            for x in range(0, width):
                if ocean[y][x]:
                    all_land -= 1
    desired_land = all_land * land_perc
    return search(0, 255, desired_land)


def find_threshold_f(elevation, land_perc, ocean=None):
    width = len(elevation[0])
    height = len(elevation)
    if ocean:
        if (width != len(ocean[0])) or (height != len(ocean)):
            raise Exception(
                "Dimension of elevation and ocean do not match. Elevation is %d x %d, while ocean is %d x%d" % (
                    width, height, len(ocean[0]), len(ocean)))

    def count(e):
        tot = 0
        for y in range(0, height):
            for x in range(0, width):
                if elevation[y][x] > e and (ocean == None or not ocean[y][x]):
                    tot += 1
        return tot

    def search(a, b, desired):
        if a == b:
            return a
        if abs(b - a) < 0.005:
            ca = count(a)
            cb = count(b)
            dista = abs(desired - ca)
            distb = abs(desired - cb)
            if dista < distb:
                return a
            else:
                return b
        m = (a + b) / 2.0
        cm = count(m)
        if desired < cm:
            return search(m, b, desired)
        else:
            return search(a, m, desired)

    all_land = width * height
    if ocean:
        for y in range(0, height):
            for x in range(0, width):
                if ocean[y][x]:
                    all_land -= 1
    desired_land = all_land * land_perc
    return search(-1000.0, 1000.0, desired_land)

