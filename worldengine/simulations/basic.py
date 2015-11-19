import numpy


def find_threshold(map_data, land_percentage, ocean=None):#never used anywhere?
    height, width = map_data.shape

    #maybe map was already masked when we got it; if not, this will make sure we operate on a mask
    mask = numpy.ma.array(map_data, mask = False, keep_mask = True)

    if ocean is not None:
        if ocean.shape != map_data.shape:
            raise Exception(
                "Dimension of map and ocean do not match. " +
                "Map is %d x %d, while ocean is %d x%d" % (
                    width, height, ocean.shape[1], ocean.shape[0]))
        mask = numpy.ma.array(mask, mask = ocean, keep_mask = True)

    def count(e):
        return numpy.ma.masked_less_equal(mask, e).count()

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

    all_land = mask.count()
    desired_land = all_land * land_percentage
    return search(0, 255, desired_land)


def find_threshold_f(map_data, land_perc, ocean=None, max=1000.0, mindist=0.005):
    height, width = map_data.shape
    
    #maybe map was already masked when we got it; if not, this will make sure we operate on a mask
    mask = numpy.ma.array(map_data, mask = False, keep_mask = True)

    if ocean is not None:
        if ocean.shape != map_data.shape:
            raise Exception(
                "Dimension of map_data and ocean do not match. " +
                "Map is %d x %d, while ocean is %d x%d" % (
                    width, height, ocean.shape[1], ocean.shape[0]))
        mask = numpy.ma.array(mask, mask = ocean, keep_mask = True)

    def count(e):
        return numpy.ma.masked_less_equal(mask, e).count()

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

    all_land = mask.count()
    desired_land = all_land * land_perc
    return search(-1*max, max, desired_land)
