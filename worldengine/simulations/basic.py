import numpy

def find_threshold(elevation, land_percentage, ocean=None):
    #never used anywhere? will serve as a numpy-example for the method below
    height, width = elevation.shape

    def count(e):
        mask = elevation
        if ocean is not None:
            mask = numpy.ma.array(elevation, mask = ocean)
        mask = numpy.ma.masked_less_equal(mask, e)

        return mask.count()

    def search(a, b, desired):
        if (not type(a) == int) or (not type(b) == int):
            raise Exception("A and B should be int")
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
	    all_land -= numpy.count_nonzero(ocean)
    desired_land = all_land * land_percentage
    return search(0, 255, desired_land)


def find_threshold_f(elevation, land_perc, ocean=None, max=1000.0, mindist=0.0001):
    #by far not only used for elevation maps! TODO: use numpy once all maps are numpy arrays
    width = len(elevation[0])
    height = len(elevation)
    if ocean is not None:
        if width != ocean.shape[1] or (height != ocean.shape[0]):
            raise Exception(
                "Dimension of elevation and ocean do not match. " +
                "Elevation is %d x %d, while ocean is %d x%d" % (
                    width, height, ocean.shape[1], ocean.shape[0]))

    def count(e):
        tot = 0
        for y in range(0, height):
            for x in range(0, width):
                if elevation[y][x] > e and (ocean is None or not ocean[y, x]):
                    tot += 1
        return tot

    def search(a, b, desired):
        if a == b:
            return a
        if abs(b - a) < mindist:
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
    if ocean is not None:
	    all_land -= numpy.count_nonzero(ocean)
    desired_land = all_land * land_perc
    return search(-1*max, max, desired_land)
