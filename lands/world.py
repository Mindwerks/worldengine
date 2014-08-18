__author__ = 'Federico Tomassetti'

from biome import *
import pickle
from basic_map_operations import *


class World(object):

    def __init__(self, name, width, height):
        self.name = name
        self.width = width
        self.height = height

    def is_mountain(self, pos):
        if not self.is_land(pos):
            return False
        if len(self.elevation['thresholds']) == 4:
            mi = 2
        else:
            mi = 1
        mountain_level = self.elevation['thresholds'][mi][1]
        x, y = pos
        return self.elevation['data'][y][x] > mountain_level

    def is_low_mountain(self, pos):
        if not self.is_mountain(pos):
            return False
        if len(self.elevation['thresholds']) == 4:
            mi = 2
        else:
            mi = 1
        mountain_level = self.elevation['thresholds'][mi][1]
        x, y = pos
        return self.elevation['data'][y][x] < mountain_level + 2.0

    def level_of_mountain(self, pos):
        if not self.is_land(pos):
            return False
        if len(self.elevation['thresholds']) == 4:
            mi = 2
        else:
            mi = 1
        mountain_level = self.elevation['thresholds'][mi][1]
        x, y = pos
        if self.elevation['data'][y][x] <= mountain_level:
            return 0
        else:
            return self.elevation['data'][y][x] - mountain_level

    def is_high_mountain(self, pos):
        if not self.is_mountain(pos):
            return False
        if len(self.elevation['thresholds']) == 4:
            mi = 2
        else:
            mi = 1
        mountain_level = self.elevation['thresholds'][mi][1]
        x, y = pos
        return self.elevation['data'][y][x] > mountain_level + 4.0

    def is_hill(self, pos):
        if not self.is_land(pos):
            return False
        if len(self.elevation['thresholds']) == 4:
            hi = 1
        else:
            hi = 0
        hill_level = self.elevation['thresholds'][hi][1]
        mountain_level = self.elevation['thresholds'][hi + 1][1]
        x, y = pos
        return self.elevation['data'][y][x] > hill_level and self.elevation['data'][y][x] < mountain_level

    def is_temperature_very_low(self, pos):
        th_max = self.temperature['thresholds'][0][1]
        x, y = pos
        t = self.temperature['data'][y][x]
        return t < th_max

    def is_temperature_low(self, pos):
        th_min = self.temperature['thresholds'][0][1]
        th_max = self.temperature['thresholds'][1][1]
        x, y = pos
        t = self.temperature['data'][y][x]
        return t < th_max and t >= th_min

    def is_temperature_medium(self, pos):
        th_min = self.temperature['thresholds'][1][1]
        th_max = self.temperature['thresholds'][2][1]
        x, y = pos
        t = self.temperature['data'][y][x]
        return t < th_max and t >= th_min

    def is_temperature_high(self, pos):
        th_min = self.temperature['thresholds'][2][1]
        x, y = pos
        t = self.temperature['data'][y][x]
        return t >= th_min

    def is_humidity_very_low(self, pos):
        th_max = self.humidity['quantiles']['75']
        # print('Humidity Q10 %f' % th_max)
        x, y = pos
        t = self.humidity['data'][y][x]
        return t < th_max

    def is_humidity_low(self, pos):
        th_min = self.humidity['quantiles']['75']
        th_max = self.humidity['quantiles']['66']
        # print('Humidity Q10 %f' % th_min)
        #print('Humidity Q33 %f' % th_max)
        x, y = pos
        t = self.humidity['data'][y][x]
        return t < th_max and t >= th_min

    def is_humidity_medium(self, pos):
        th_min = self.humidity['quantiles']['66']
        th_max = self.humidity['quantiles']['33']
        # print('Humidity Q33 %f' % th_min)
        #print('Humidity Q66 %f' % th_max)
        x, y = pos
        t = self.humidity['data'][y][x]
        return t < th_max and t >= th_min

    def is_humidity_above_quantile(self, pos, q):
        th = self.humidity['quantiles'][str(q)]
        x, y = pos
        v = self.humidity['data'][y][x]
        return v >= th

    def is_humidity_high(self, pos):
        th_min = self.humidity['quantiles']['33']
        th_max = self.humidity['quantiles']['10']
        # print('Humidity Q66 %f' % th_min)
        #print('Humidity Q75 %f' % th_max)
        x, y = pos
        t = self.humidity['data'][y][x]
        return t >= th_min and t < th_max

    def is_humidity_very_high(self, pos):
        th_min = self.humidity['quantiles']['10']
        # print('Humidity Q75 %f' % th_min)
        x, y = pos
        t = self.humidity['data'][y][x]
        return t >= th_min

    def set_biome(self, biome):
        if len(biome) != self.height:
            raise Exception("Setting data with wrong height")
        if len(biome[0]) != self.width:
            raise Exception("Setting data with wrong width")

        self.biome = biome

    def set_ocean(self, ocean):
        if (len(ocean) != self.height) or (len(ocean[0]) != self.width):
            raise Exception("Setting ocean map with wrong dimension. Expected %d x %d, found %d x %d" % (
            self.width, self.height, len(ocean[0]), len(ocean)))

        self.ocean = ocean

    def set_elevation(self, data, thresholds):
        if (len(data) != self.height) or (len(data[0]) != self.width):
            raise Exception("Setting elevation map with wrong dimension. Expected %d x %d, found %d x %d" % (
            self.width, self.height, (len[data[0]], len(data))))
        self.elevation = {'data': data, 'thresholds': thresholds}

    def set_precipitation(self, data, thresholds):
        """"Precipitation is a value in [-1,1]"""

        if len(data) != self.height:
            raise Exception("Setting data with wrong height")
        if len(data[0]) != self.width:
            raise Exception("Setting data with wrong width")

        self.precipitation = {'data': data, 'thresholds': thresholds}

    def set_temperature(self, data, thresholds):
        if len(data) != self.height:
            raise Exception("Setting data with wrong height")
        if len(data[0]) != self.width:
            raise Exception("Setting data with wrong width")

        self.temperature = {'data': data, 'thresholds': thresholds}

    def set_permeability(self, data, thresholds):
        if len(data) != self.height:
            raise Exception("Setting data with wrong height")
        if len(data[0]) != self.width:
            raise Exception("Setting data with wrong width")

        self.permeability = {'data': data, 'thresholds': thresholds}

    def contains_stream(self, pos):
        return self.contains_creek(pos) or self.contains_river(pos) or self.contains_main_river(pos)

    def contains_creek(self, pos):
        x, y = pos
        v = self.watermap['data'][y][x]
        return v >= self.watermap['thresholds']['creek'] and v < self.watermap['thresholds']['river']

    def contains_river(self, pos):
        x, y = pos
        v = self.watermap['data'][y][x]
        return v >= self.watermap['thresholds']['river'] and v < self.watermap['thresholds']['main river']

    def contains_main_river(self, pos):
        x, y = pos
        v = self.watermap['data'][y][x]
        return v >= self.watermap['thresholds']['main river']

    def random_land(self):
        x, y = random_point(self.width, self.height)
        if self.ocean[y][x]:
            return self.random_land()
        else:
            return (x, y)

    def is_land(self, pos):
        x, y = pos
        return not self.ocean[y][x]

    def is_ocean(self, pos):
        x, y = pos
        return self.ocean[y][x]

    def on_tiles_around_factor(self, factor, pos, radius=1, action=None):
        x, y = pos
        for dx in range(-radius, radius + 1):
            nx = x + dx
            if nx >= 0 and nx/factor < self.width:
                for dy in range(-radius, radius + 1):
                    ny = y + dy
                    if ny >= 0 and ny/factor < self.height and (dx != 0 or dy != 0):
                        action((nx, ny))


    def on_tiles_around(self, pos, radius=1, action=None):
        x, y = pos
        for dx in range(-radius, radius + 1):
            nx = x + dx
            if nx >= 0 and nx < self.width:
                for dy in range(-radius, radius + 1):
                    ny = y + dy
                    if ny >= 0 and ny < self.height and (dx != 0 or dy != 0):
                        action((nx, ny))

    def tiles_around(self, pos, radius=1, predicate=None):
        ps = []
        x, y = pos
        for dx in range(-radius, radius + 1):
            nx = x + dx
            if nx >= 0 and nx < self.width:
                for dy in range(-radius, radius + 1):
                    ny = y + dy
                    if ny >= 0 and ny < self.height and (dx != 0 or dy != 0):
                        if predicate == None or predicate((nx, ny)):
                            ps.append((nx, ny))
        return ps

    def tiles_around_factor(self, factor, pos, radius=1, predicate=None):
        ps = []
        x, y = pos
        for dx in range(-radius, radius + 1):
            nx = x + dx
            if nx >= 0 and nx < self.width*factor:
                for dy in range(-radius, radius + 1):
                    ny = y + dy
                    if ny >= 0 and ny < self.height*factor and (dx != 0 or dy != 0):
                        if predicate == None or predicate((nx, ny)):
                            ps.append((nx, ny))
        return ps

    def tiles_around_many(self, pos_list, radius=1, predicate=None):
        tiles = []
        for pos in pos_list:
            tiles += self.tiles_around(pos, radius, predicate)
        # remove duplicates
        # remove elements in pos
        return list(set(tiles) - set(pos_list))

    def watermap_at(self, pos):
        x, y = pos
        return self.watermap['data'][y][x]

    def biome_at(self, pos):
        x, y = pos
        b = Biome.by_name(self.biome[y][x])
        if b == None:
            raise Exception('Not found')
        return b

    def is_forest(self, pos):
        return isinstance(self.biome_at(pos), Forest)

    def is_tundra(self, pos):
        return isinstance(self.biome_at(pos), Tundra)

    def is_glacier(self, pos):
        return isinstance(self.biome_at(pos), Glacier)

    def is_iceland(self, pos):
        return isinstance(self.biome_at(pos), Iceland)

    def is_jungle(self, pos):
        return isinstance(self.biome_at(pos), Jungle)

    def is_savanna(self, pos):
        return isinstance(self.biome_at(pos), Savanna)

    def is_sand_desert(self, pos):
        return isinstance(self.biome_at(pos), SandDesert)

    def is_rock_desert(self, pos):
        return isinstance(self.biome_at(pos), RockDesert)

    def sustainable_population(self, pos):
        return self.biome_at(pos).sustainable_population

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @classmethod
    def from_pickle_file(cls, filename):
        with open(filename, "r") as f:
            return pickle.load(f)

    @classmethod
    def from_dict(cls, dict):
        instance = World(dict['name'], dict['width'], dict['height'])
        for k in dict:
            instance.__dict__[k] = dict[k]
        return instance
