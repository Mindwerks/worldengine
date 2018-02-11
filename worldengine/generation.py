import numpy
import time

from noise import snoise2
from worldengine.common import anti_alias
from worldengine.simulations.basic import find_threshold_f
# ------------------
# Initial generation
# ------------------

def calculate_minium_map_sums(data):
    
    x_sums = data.sum(0)  # 0 == sum along y-axis
    x_with_min_sum = x_sums.argmin()
    
    y_sums = data.sum(1)  # 1 == sum along x-axis
    y_with_min_sum = y_sums.argmin()
            
    return y_with_min_sum,x_with_min_sum

def center_map(data,delta_y,delta_x):
    
    data=numpy.roll(data, -delta_y, axis=0)
    data=numpy.roll(data, -delta_x, axis=1)
    
    return data

def center_land(elevation,plate_map,verbose=False):
    """Translate the map horizontally and vertically to put as much ocean as
       possible at the borders. 
       
       It takes two numpy matrices representing the elevation and plate map, 
       calculates the minimum sum and rolls both accordingly"""
    
    delta_y , delta_x = calculate_minium_map_sums(elevation)
    
    new_elevation = center_map(elevation,delta_y,delta_x)
    new_plate_map = center_map(plate_map,delta_y,delta_x)
    
    if verbose:
        print("center land complete")
        
    return new_elevation, new_plate_map

def place_oceans_at_map_borders(input_data):
    #this function lowers the values the matrix at the edges
    #maybe this has some other uses?
    #can't think of any right now, so I'll keep the name.
    """
    Lower the elevation near the border of the map
    """
    
    height,width=input_data.shape
    ocean_border = int(min(30, max(width / 5, height / 5) ) )
    

    for x in range(width):
        for i in range(ocean_border):
            place_ocean(input_data,ocean_border,x, i, i)
            place_ocean(input_data,ocean_border,x, height - i - 1, i)

    for y in range(height):
        for i in range(ocean_border):
            place_ocean(input_data,ocean_border,i, y, i)
            place_ocean(input_data,ocean_border,width - i - 1, y, i)
    return input_data
    
def place_ocean(input_data,ocean_border,x, y, i):
    input_data[y, x] = (input_data[y, x] * i) / ocean_border

def add_noise_to_matrix(input_matrix, seed):
    
    #this has probably more uses than just elevation noise!
    
    octaves = 8
    freq = 16.0 * octaves
    size=input_matrix.shape
    height,width=size
    print("shape",size)
    
    for y in range(height):
        for x in range(width):
            n = snoise2(x / freq * 2, y / freq * 2, octaves, base=seed)
            input_matrix[y, x] += n
            
    return input_matrix


def fill_ocean(elevation, sea_level):#TODO: Make more use of numpy?
    height, width = elevation.shape

    ocean = numpy.zeros(elevation.shape, dtype=bool)
    to_expand = []
    for x in range(width):#handle top and bottom border of the map
        if elevation[0, x] <= sea_level:
            to_expand.append((x, 0))
        if elevation[height - 1, x] <= sea_level:
            to_expand.append((x, height - 1))
    for y in range(height):#handle left- and rightmost border of the map
        if elevation[y, 0] <= sea_level:
            to_expand.append((0, y))
        if elevation[y, width - 1] <= sea_level:
            to_expand.append((width - 1, y))
    for t in to_expand:
        tx, ty = t
        if not ocean[ty, tx]:
            ocean[ty, tx] = True
            for px, py in _around(tx, ty, width, height):
                if not ocean[py, px] and elevation[py, px] <= sea_level:
                    to_expand.append((px, py))

    return ocean


def initialize_ocean_and_thresholds(e, ocean_level=1.0):
    """
    Calculate the ocean, the sea depth and the elevation thresholds
    :param world: a world having elevation but not thresholds
    :param ocean_level: the elevation representing the ocean level
    :return: nothing, the world will be changed
    """
    
    #e = 
    ocean = fill_ocean(e, ocean_level)
    hl = find_threshold_f(e, 0.10)  # the highest 10% of all (!) land are declared hills
    ml = find_threshold_f(e, 0.03)  # the highest 3% are declared mountains
    e_th = [('sea', ocean_level),
            ('plain', hl),
            ('hill', ml),
            ('mountain', None)]
    harmonize_ocean(ocean, e, ocean_level)
    
    return ocean, ocean_level, (e,e_th)
   


def harmonize_ocean(ocean, elevation, ocean_level):
    """
    The goal of this function is to make the ocean floor less noisy.
    The underwater erosion should cause the ocean floor to be more uniform
    """

    shallow_sea = ocean_level * 0.85
    midpoint = shallow_sea / 2.0

    ocean_points = numpy.logical_and(elevation < shallow_sea, ocean)

    shallow_ocean = numpy.logical_and(elevation < midpoint, ocean_points)
    elevation[shallow_ocean] = midpoint - ((midpoint - elevation[shallow_ocean]) / 5.0)

    deep_ocean = numpy.logical_and(elevation > midpoint, ocean_points)
    elevation[deep_ocean] = midpoint + ((elevation[deep_ocean] - midpoint) / 5.0)

# ----
# Misc
# ----

def sea_depth(world, sea_level):

    # a dynamic programming approach to gather how far the next land is 
    # from a given coordinate up to a maximum distance of max_radius
    # result is 0 for land coordinates and -1 for coordinates further than
    # max_radius away from land
    # there might be even faster ways but it does the trick

    def next_land_dynamic(ocean, max_radius=5):
    
        next_land = numpy.full(ocean.shape, -1, int)

        # non ocean tiles are zero distance away from next land
        next_land[numpy.logical_not(ocean)]=0

        height, width = ocean.shape

        for dist in range(max_radius):
            indices = numpy.transpose(numpy.where(next_land==dist))
            for y, x in indices:
                for dy in range(-1, 2):
                    ny = y + dy
                    if 0 <= ny < height:
                        for dx in range(-1, 2):
                            nx = x + dx
                            if 0 <= nx < width:
                                if next_land[ny,nx] == -1:
                                    next_land[ny,nx] = dist + 1
        return next_land

    # We want to multiply the raw sea_depth by one of these factors 
    # depending on the distance from the next land
    # possible TODO: make this a parameter
    factors = [0.0, 0.3, 0.5, 0.7, 0.9]

    next_land = next_land_dynamic(world.layers['ocean'].data)

    sea_depth = sea_level - world.layers['elevation'].data

    for y in range(world.height):
        for x in range(world.width):
            dist_to_next_land = next_land[y,x]
            if dist_to_next_land > 0:
                sea_depth[y,x]*=factors[dist_to_next_land-1]

    sea_depth = anti_alias(sea_depth, 10)

    min_depth = sea_depth.min()
    max_depth = sea_depth.max()
    sea_depth = (sea_depth - min_depth) / (max_depth - min_depth)

    return sea_depth


def _around(x, y, width, height):
    ps = []
    for dx in range(-1, 2):
        nx = x + dx
        if 0 <= nx < width:
            for dy in range(-1, 2):
                ny = y + dy
                if 0 <= ny < height and (dx != 0 or dy != 0):
                    ps.append((nx, ny))
    return ps
