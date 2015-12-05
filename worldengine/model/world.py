import numpy

from worldengine.biome import *
from worldengine.common import _equal
from worldengine.version import __version__


class Size(object):

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False


class GenerationParameters(object):

    def __init__(self, n_plates, ocean_level, step):
        self.n_plates = n_plates
        self.ocean_level = ocean_level
        self.step = step

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False


class Layer(object):

    def __init__(self, data):
        self.data = data

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return _equal(self.data, other.data)
        else:
            return False

    def min(self):
        return self.data.min()

    def max(self):
        return self.data.max()


class LayerWithThresholds(Layer):

    def __init__(self, data, thresholds):
        Layer.__init__(self, data)
        self.thresholds = thresholds

    def __eq__(self, other):
        if isinstance(other, self.__class__):

            return _equal(self.data, other.data) and _equal(self.thresholds, other.thresholds)
        else:
            return False


class LayerWithQuantiles(Layer):

    def __init__(self, data, quantiles):
        Layer.__init__(self, data)
        self.quantiles = quantiles

    def __eq__(self, other):
        if isinstance(other, self.__class__):

            return _equal(self.data, other.data) and _equal(self.quantiles, other.quantiles)
        else:
            return False


class World(object):
    """A world composed by name, dimensions and all the characteristics of
    each cell.
    """

    def __init__(self, name, size, seed, generation_params,
                 temps=[0.874, 0.765, 0.594, 0.439, 0.366, 0.124],
                 humids = [.941, .778, .507, .236, 0.073, .014, .002],
                 gamma_curve=1.25, curve_offset=.2):
        self.name = name
        self.size = size
        self.seed = seed
        self.temps = temps
        self.humids = humids
        self.gamma_curve = gamma_curve
        self.curve_offset = curve_offset

        self.generation_params = generation_params

        self.layers = {}

        # Deprecated
        self.width = size.width
        self.height = size.height
        self.n_plates = generation_params.n_plates
        self.step = generation_params.step
        self.ocean_level = generation_params.ocean_level

    #
    # General methods
    #

    def __eq__(self, other):
        return _equal(self.__dict__, other.__dict__)

    #
    # Serialization / Unserialization
    #

    @classmethod
    def from_dict(cls, dict):
        instance = World(dict['name'], Size(dict['width'], dict['height']))
        for k in dict:
            instance.__dict__[k] = dict[k]
        return instance

    @staticmethod
    def worldengine_tag():
        return ord('W') * (256 ** 3) + ord('o') * (256 ** 2) + \
            ord('e') * (256 ** 1) + ord('n')

    @staticmethod
    def __version_hashcode__():
        parts = __version__.split('.')
        return int(parts[0])*(256**3) + int(parts[1])*(256**2) + int(parts[2])*(256**1)

    #
    # General
    #

    def contains(self, pos):
        return 0 <= pos[0] < self.width and 0 <= pos[1] < self.height

    #
    # Land/Ocean
    #

    def random_land(self):
        if self.ocean.data.all():
            return None, None  # return invalid indices if there is no land at all
        lands = numpy.invert(self.ocean.data)
        lands = numpy.transpose(lands.nonzero())  # returns a list of tuples/indices with land positions
        y, x = lands[numpy.random.randint(0, len(lands))]  # uses global RNG
        return x, y

    def is_land(self, pos):
        return not self.ocean.data[pos[1], pos[0]]#faster than reversing pos or transposing ocean

    def is_ocean(self, pos):
        return self.ocean.data[pos[1], pos[0]]

    def sea_level(self):
        return self.elevation.thresholds[0][1]

    #
    # Tiles around
    #

    def on_tiles_around_factor(self, factor, pos, action, radius=1):
        x, y = pos
        for dx in range(-radius, radius + 1):
            nx = x + dx
            if nx >= 0 and nx / factor < self.width:
                for dy in range(-radius, radius + 1):
                    ny = y + dy
                    if ny >= 0 and ny / factor < self.height and (
                                    dx != 0 or dy != 0):
                        action((nx, ny))

    def on_tiles_around(self, pos, action, radius=1):
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
            if 0 <= nx < self.width:
                for dy in range(-radius, radius + 1):
                    ny = y + dy
                    if 0 <= ny < self.height and (dx != 0 or dy != 0):
                        if predicate is None or predicate((nx, ny)):
                            ps.append((nx, ny))
        return ps

    def tiles_around_factor(self, factor, pos, radius=1, predicate=None):
        ps = []
        x, y = pos
        for dx in range(-radius, radius + 1):
            nx = x + dx
            if nx >= 0 and nx < self.width * factor:
                for dy in range(-radius, radius + 1):
                    ny = y + dy
                    if ny >= 0 and ny < self.height * factor and (
                            dx != 0 or dy != 0):
                        if predicate is None or predicate((nx, ny)):
                            ps.append((nx, ny))
        return ps

    def tiles_around_many(self, pos_list, radius=1, predicate=None):
        tiles = []
        for pos in pos_list:
            tiles += self.tiles_around(pos, radius, predicate)
        # remove duplicates
        # remove elements in pos
        return list(set(tiles) - set(pos_list))

    #
    # Elevation
    #

    def start_mountain_th(self):
        return self.elevation.thresholds[2][1]

    def is_mountain(self, pos):
        if self.is_ocean(pos):
            return False
        if len(self.elevation.thresholds) == 4:
            mi = 2
        else:
            mi = 1
        mountain_level = self.elevation.thresholds[mi][1]
        x, y = pos
        return self.elevation.data[y][x] > mountain_level

    def is_low_mountain(self, pos):
        if not self.is_mountain(pos):
            return False
        if len(self.elevation.thresholds) == 4:
            mi = 2
        else:
            mi = 1
        mountain_level = self.elevation.thresholds[mi][1]
        x, y = pos
        return self.elevation.data[y, x] < mountain_level + 2.0

    def level_of_mountain(self, pos):
        if self.is_ocean(pos):
            return False
        if len(self.elevation.thresholds) == 4:
            mi = 2
        else:
            mi = 1
        mountain_level = self.elevation.thresholds[mi][1]
        x, y = pos
        if self.elevation.data[y, x] <= mountain_level:
            return 0
        else:
            return self.elevation.data[y, x] - mountain_level

    def is_high_mountain(self, pos):
        if not self.is_mountain(pos):
            return False
        if len(self.elevation.thresholds) == 4:
            mi = 2
        else:
            mi = 1
        mountain_level = self.elevation.thresholds[mi][1]
        x, y = pos
        return self.elevation.data[y, x] > mountain_level + 4.0

    def is_hill(self, pos):
        if self.is_ocean(pos):
            return False
        if len(self.elevation.thresholds) == 4:
            hi = 1
        else:
            hi = 0
        hill_level = self.elevation.thresholds[hi][1]
        mountain_level = self.elevation.thresholds[hi + 1][1]
        x, y = pos
        return hill_level < self.elevation.data[y, x] < mountain_level

    def elevation_at(self, pos):
        return self.elevation.data[pos[1], pos[0]]

    #
    # Precipitations
    #

    def precipitations_at(self, pos):
        x, y = pos
        return self.precipitation.data[y, x]

    def precipitations_thresholds(self):
        return self.precipitation.thresholds

    #
    # Temperature
    #

    def is_temperature_polar(self, pos):
        th_max = self.temperature.thresholds[0][1]
        x, y = pos
        t = self.temperature.data[y, x]
        return t < th_max

    def is_temperature_alpine(self, pos):
        th_min = self.temperature.thresholds[0][1]
        th_max = self.temperature.thresholds[1][1]
        x, y = pos
        t = self.temperature.data[y, x]
        return th_max > t >= th_min

    def is_temperature_boreal(self, pos):
        th_min = self.temperature.thresholds[1][1]
        th_max = self.temperature.thresholds[2][1]
        x, y = pos
        t = self.temperature.data[y, x]
        return th_max > t >= th_min

    def is_temperature_cool(self, pos):
        th_min = self.temperature.thresholds[2][1]
        th_max = self.temperature.thresholds[3][1]
        x, y = pos
        t = self.temperature.data[y, x]
        return th_max > t >= th_min

    def is_temperature_warm(self, pos):
        th_min = self.temperature.thresholds[3][1]
        th_max = self.temperature.thresholds[4][1]
        x, y = pos
        t = self.temperature.data[y, x]
        return th_max > t >= th_min

    def is_temperature_subtropical(self, pos):
        th_min = self.temperature.thresholds[4][1]
        th_max = self.temperature.thresholds[5][1]
        x, y = pos
        t = self.temperature.data[y, x]
        return th_max > t >= th_min

    def is_temperature_tropical(self, pos):
        th_min = self.temperature.thresholds[5][1]
        x, y = pos
        t = self.temperature.data[y, x]
        return t >= th_min

    def temperature_at(self, pos):
        x, y = pos
        return self.temperature.data[y, x]

    def temperature_thresholds(self):
        return self.temperature.thresholds

    #
    # Humidity
    #

    def humidity_at(self, pos):
        x, y = pos
        return self.humidity.data[y, x]

    def is_humidity_above_quantile(self, pos, q):
        th = self.humidity.quantiles[str(q)]
        x, y = pos
        t = self.humidity.data[y, x]
        return t >= th

    def is_humidity_superarid(self, pos):
        th_max = self.humidity.quantiles['87']
        x, y = pos
        t = self.humidity.data[y, x]
        return t < th_max

    def is_humidity_perarid(self, pos):
        th_min = self.humidity.quantiles['87']
        th_max = self.humidity.quantiles['75']
        x, y = pos
        t = self.humidity.data[y, x]
        return th_max > t >= th_min

    def is_humidity_arid(self, pos):
        th_min = self.humidity.quantiles['75']
        th_max = self.humidity.quantiles['62']
        x, y = pos
        t = self.humidity.data[y, x]
        return th_max > t >= th_min

    def is_humidity_semiarid(self, pos):
        th_min = self.humidity.quantiles['62']
        th_max = self.humidity.quantiles['50']
        x, y = pos
        t = self.humidity.data[y, x]
        return th_max > t >= th_min

    def is_humidity_subhumid(self, pos):
        th_min = self.humidity.quantiles['50']
        th_max = self.humidity.quantiles['37']
        x, y = pos
        t = self.humidity.data[y, x]
        return th_max > t >= th_min

    def is_humidity_humid(self, pos):
        th_min = self.humidity.quantiles['37']
        th_max = self.humidity.quantiles['25']
        x, y = pos
        t = self.humidity.data[y, x]
        return th_max > t >= th_min

    def is_humidity_perhumid(self, pos):
        th_min = self.humidity.quantiles['25']
        th_max = self.humidity.quantiles['12']
        x, y = pos
        t = self.humidity.data[y, x]
        return th_max > t >= th_min

    def is_humidity_superhumid(self, pos):
        th_min = self.humidity.quantiles['12']
        x, y = pos
        t = self.humidity.data[y, x]
        return t >= th_min

    #
    # Streams
    #

    def contains_stream(self, pos):
        return self.contains_creek(pos) or self.contains_river(
            pos) or self.contains_main_river(pos)

    def contains_creek(self, pos):
        x, y = pos
        v = self.watermap['data'][y, x]
        return self.watermap['thresholds']['creek'] <= v < \
            self.watermap['thresholds']['river']

    def contains_river(self, pos):
        x, y = pos
        v = self.watermap['data'][y, x]
        return self.watermap['thresholds']['river'] <= v < \
            self.watermap['thresholds']['main river']

    def contains_main_river(self, pos):
        x, y = pos
        v = self.watermap['data'][y, x]
        return v >= self.watermap['thresholds']['main river']

    def watermap_at(self, pos):
        x, y = pos
        return self.watermap['data'][y, x]

    #
    # Biome
    #

    def biome_at(self, pos):
        x, y = pos
        b = Biome.by_name(self.biome.data[y, x])
        if b is None:
            raise Exception('Not found')
        return b

    def is_boreal_forest(self, pos):
        if isinstance(self.biome_at(pos), BorealMoistForest):
            return True
        elif isinstance(self.biome_at(pos), BorealWetForest):
            return True
        elif isinstance(self.biome_at(pos), BorealRainForest):
            return True
        else:
            return False

    def is_temperate_forest(self, pos):
        if isinstance(self.biome_at(pos), CoolTemperateMoistForest):
            return True
        elif isinstance(self.biome_at(pos), CoolTemperateWetForest):
            return True
        elif isinstance(self.biome_at(pos), CoolTemperateRainForest):
            return True
        else:
            return False

    def is_warm_temperate_forest(self, pos):
        if isinstance(self.biome_at(pos), WarmTemperateMoistForest):
            return True
        elif isinstance(self.biome_at(pos), WarmTemperateWetForest):
            return True
        elif isinstance(self.biome_at(pos), WarmTemperateRainForest):
            return True
        else:
            return False

    def is_tropical_dry_forest(self, pos):
        if isinstance(self.biome_at(pos), SubtropicalDryForest):
            return True
        elif isinstance(self.biome_at(pos), TropicalDryForest):
            return True
        else:
            return False

    def is_tundra(self, pos):
        if isinstance(self.biome_at(pos), SubpolarMoistTundra):
            return True
        elif isinstance(self.biome_at(pos), SubpolarWetTundra):
            return True
        elif isinstance(self.biome_at(pos), SubpolarRainTundra):
            return True
        else:
            return False

    def is_iceland(self, pos):
        if isinstance(self.biome_at(pos), Ice):
            return True
        elif isinstance(self.biome_at(pos), PolarDesert):
            return True
        else:
            return False

    def is_jungle(self, pos):
        if isinstance(self.biome_at(pos), SubtropicalMoistForest):
            return True
        elif isinstance(self.biome_at(pos), SubtropicalWetForest):
            return True
        elif isinstance(self.biome_at(pos), SubtropicalRainForest):
            return True
        elif isinstance(self.biome_at(pos), TropicalMoistForest):
            return True
        elif isinstance(self.biome_at(pos), TropicalWetForest):
            return True
        elif isinstance(self.biome_at(pos), TropicalRainForest):
            return True
        else:
            return False

    def is_savanna(self, pos):
        if isinstance(self.biome_at(pos), SubtropicalThornWoodland):
            return True
        elif isinstance(self.biome_at(pos), TropicalThornWoodland):
            return True
        elif isinstance(self.biome_at(pos), TropicalVeryDryForest):
            return True
        else:
            return False

    def is_hot_desert(self, pos):
        if isinstance(self.biome_at(pos), WarmTemperateDesert):
            return True
        elif isinstance(self.biome_at(pos), WarmTemperateDesertScrub):
            return True
        elif isinstance(self.biome_at(pos), SubtropicalDesert):
            return True
        elif isinstance(self.biome_at(pos), SubtropicalDesertScrub):
            return True
        elif isinstance(self.biome_at(pos), TropicalDesert):
            return True
        elif isinstance(self.biome_at(pos), TropicalDesertScrub):
            return True
        else:
            return False

    def is_cold_parklands(self, pos):
        if isinstance(self.biome_at(pos), SubpolarDryTundra):
            return True
        elif isinstance(self.biome_at(pos), BorealDesert):
            return True
        elif isinstance(self.biome_at(pos), BorealDryScrub):
            return True
        else:
            return False

    def is_steppe(self, pos):
        if isinstance(self.biome_at(pos), CoolTemperateSteppe):
            return True
        else:
            return False

    def is_cool_desert(self, pos):
        if isinstance(self.biome_at(pos), CoolTemperateDesert):
            return True
        elif isinstance(self.biome_at(pos), CoolTemperateDesertScrub):
            return True
        else:
            return False

    def is_chaparral(self, pos):
        """ Chaparral is a shrubland or heathland plant community.

        For details see http://en.wikipedia.org/wiki/Chaparral.
        """
        if isinstance(self.biome_at(pos), WarmTemperateThornScrub):
            return True
        elif isinstance(self.biome_at(pos), WarmTemperateDryForest):
            return True
        else:
            return False

    #
    # Plates
    #

    def n_actual_plates(self):
        return self.plates.data.max() + 1

    #
    # Accessors
    #

    @property
    def elevation(self):
        return self.layers['elevation']

    @property
    def plates(self):
        return self.layers['plates']

    @property
    def biome(self):
        return self.layers['biome']

    @property
    def ocean(self):
        return self.layers['ocean']

    @property
    def precipitation(self):
        return self.layers['precipitation']

    @property
    def sea_depth(self):
        return self.layers['sea_depth']

    @property
    def humidity(self):
        return self.layers['humidity']

    @property
    def irrigation(self):
        return self.layers['irrigation']

    @property
    def temperature(self):
        return self.layers['temperature']

    @property
    def permeability(self):
        return self.layers['permeability']

    @property
    def watermap(self):
        return self.layers['watermap']

    @property
    def river_map(self):
        return self.layers['river_map']

    @property
    def lake_map(self):
        return self.layers['lake_map']

    @property
    def icecap(self):
        return self.layers['icecap']

    #
    # Setters
    #

    def set_elevation(self, data, thresholds):
        if data.shape != (self.height, self.width):
            raise Exception(
                "Setting elevation map with wrong dimension. "
                "Expected %d x %d, found %d x %d" % (
                    self.width, self.height, data.shape[1], data.shape[0]))
        self.layers['elevation'] = LayerWithThresholds(data, thresholds)

    def set_plates(self, data):
        if (data.shape[0] != self.height) or (data.shape[1] != self.width):
            raise Exception(
                "Setting plates map with wrong dimension. "
                "Expected %d x %d, found %d x %d" % (
                    self.width, self.height, data.shape[1], data.shape[0]))
        self.layers['plates'] = Layer(data)

    def set_biome(self, biome):
        if biome.shape[0] != self.height:
            raise Exception(
                "Setting data with wrong height: biome has height %i while "
                "the height is currently %i" % (
                    biome.shape[0], self.height))
        if biome.shape[1] != self.width:
            raise Exception("Setting data with wrong width")

        self.layers['biome'] = Layer(biome)

    def set_ocean(self, ocean):
        if (ocean.shape[0] != self.height) or (ocean.shape[1] != self.width):
            raise Exception(
                "Setting ocean map with wrong dimension. Expected %d x %d, "
                "found %d x %d" % (self.width, self.height,
                                   ocean.shape[1], ocean.shape[0]))

        self.layers['ocean'] = Layer(ocean)

    def set_sea_depth(self, data):
        if (data.shape[0] != self.height) or (data.shape[1] != self.width):
            raise Exception(
                "Setting sea depth map with wrong dimension. Expected %d x %d, "
                "found %d x %d" % (self.width, self.height,
                                   data.shape[1], data.shape[0]))

        self.layers['sea_depth'] = Layer(data)

    def set_precipitation(self, data, thresholds):
        """"Precipitation is a value in [-1,1]"""

        if data.shape[0] != self.height:
            raise Exception("Setting data with wrong height")
        if data.shape[1] != self.width:
            raise Exception("Setting data with wrong width")
        self.layers['precipitation'] = LayerWithThresholds(data, thresholds)

    def set_humidity(self, data, quantiles):
        if data.shape[0] != self.height:
            raise Exception("Setting data with wrong height")
        if data.shape[1] != self.width:
            raise Exception("Setting data with wrong width")
        self.layers['humidity'] = LayerWithQuantiles(data, quantiles)

    def set_irrigation(self, data):
        if data.shape[0] != self.height:
            raise Exception("Setting data with wrong height")
        if data.shape[1] != self.width:
            raise Exception("Setting data with wrong width")

        self.layers['irrigation'] = Layer(data)

    def set_temperature(self, data, thresholds):
        if data.shape[0] != self.height:
            raise Exception("Setting data with wrong height")
        if data.shape[1] != self.width:
            raise Exception("Setting data with wrong width")
        self.layers['temperature'] = LayerWithThresholds(data, thresholds)

    def set_permeability(self, data, thresholds):
        if data.shape[0] != self.height:
            raise Exception("Setting data with wrong height")
        if data.shape[1] != self.width:
            raise Exception("Setting data with wrong width")
        self.layers['permeability'] = LayerWithThresholds(data, thresholds)

    def set_watermap(self, data, thresholds):
        if data.shape[0] != self.height:
            raise Exception("Setting data with wrong height")
        if data.shape[1] != self.width:
            raise Exception("Setting data with wrong width")
        self.layers['watermap'] = LayerWithThresholds(data, thresholds)

    def set_rivermap(self, river_map):
        self.layers['river_map'] = Layer(river_map)

    def set_lakemap(self, lake_map):
        self.layers['lake_map'] = Layer(lake_map)

    def set_icecap(self, icecap):
        self.layers['icecap'] = Layer(icecap)

    def has_ocean(self):
        return 'ocean' in self.layers

    def has_precipitations(self):
        return 'precipitation' in self.layers

    def has_watermap(self):
        return 'watermap' in self.layers

    def has_irrigation(self):
        return 'irrigation' in self.layers

    def has_humidity(self):
        return 'humidity' in self.layers

    def has_temperature(self):
        return 'temperature' in self.layers

    def has_permeability(self):
        return 'permeability' in self.layers

    def has_biome(self):
        return 'biome' in self.layers

    def has_rivermap(self):
        return 'river_map' in self.layers

    def has_lakemap(self):
        return 'lake_map' in self.layers

    def has_icecap(self):
        return 'icecap' in self.layers
