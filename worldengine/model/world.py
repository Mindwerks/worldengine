import numpy

from worldengine.biome import biome_name_to_index, biome_index_to_name, Biome
from worldengine.biome import Iceland
import worldengine.protobuf.World_pb2 as Protobuf
from worldengine.step import Step
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

    def protobuf_serialize(self):
        p_world = self._to_protobuf_world()
        return p_world.SerializeToString()

    def protobuf_to_file(self, filename):
        with open(filename, "wb") as f:
            f.write(self.protobuf_serialize())

    @staticmethod
    def open_protobuf(filename):
        with open(filename, "rb") as f:
            content = f.read()
            return World.protobuf_unserialize(content)

    @classmethod
    def protobuf_unserialize(cls, serialized):
        p_world = Protobuf.World()
        p_world.ParseFromString(serialized)
        return World._from_protobuf_world(p_world)

    @staticmethod
    def _to_protobuf_matrix(matrix, p_matrix, transformation=None):

        m = matrix
        if transformation is not None:
            t = numpy.vectorize(transformation)
            m = t(m)

        for row in m:
            p_row = p_matrix.rows.add()
            '''
            When using numpy, certain primitive types are replaced with
            numpy-specifc versions that, even though mostly compatible,
            cannot be digested by protobuf. This might change at some point;
            for now a conversion is necessary.
            '''
            p_row.cells.extend(row.tolist())

    @staticmethod
    def _to_protobuf_quantiles(quantiles, p_quantiles):
        for k in quantiles:
            entry = p_quantiles.add()
            v = quantiles[k]
            entry.key = int(k)
            entry.value = v

    @staticmethod
    def _to_protobuf_matrix_with_quantiles(matrix, p_matrix):
        World._to_protobuf_quantiles(matrix.quantiles, p_matrix.quantiles)
        World._to_protobuf_matrix(matrix.data, p_matrix)

    @staticmethod
    def _from_protobuf_matrix(p_matrix, transformation=None):
        matrix = []
        for p_row in p_matrix.rows:
            row = []
            for p_cell in p_row.cells:
                value = p_cell
                if transformation:
                    value = transformation(value)
                row.append(value)
            matrix.append(row)
        return matrix

    @staticmethod
    def _from_protobuf_quantiles(p_quantiles):
        quantiles = {}
        for p_quantile in p_quantiles:
            quantiles[str(p_quantile.key)] = p_quantile.value
        return quantiles

    @staticmethod
    def _from_protobuf_matrix_with_quantiles(p_matrix):
        data = World._from_protobuf_matrix(p_matrix)
        quantiles = World._from_protobuf_quantiles(p_matrix.quantiles)
        return data, quantiles

    @staticmethod
    def worldengine_tag():
        return ord('W') * (256 ** 3) + ord('o') * (256 ** 2) + \
            ord('e') * (256 ** 1) + ord('n')

    @staticmethod
    def __version_hashcode__():
        parts = __version__.split('.')
        return int(parts[0])*(256**3) + int(parts[1])*(256**2) + int(parts[2])*(256**1)

    def _to_protobuf_world(self):
        p_world = Protobuf.World()

        p_world.worldengine_tag = World.worldengine_tag()
        p_world.worldengine_version = self.__version_hashcode__()

        p_world.name = self.name
        p_world.width = self.width
        p_world.height = self.height

        p_world.generationData.seed = self.seed
        p_world.generationData.n_plates = self.n_plates
        p_world.generationData.ocean_level = self.ocean_level
        p_world.generationData.step = self.step.name

        # Elevation
        self._to_protobuf_matrix(self.layers['elevation'].data, p_world.heightMapData)
        p_world.heightMapTh_sea = self.layers['elevation'].thresholds[0][1]
        p_world.heightMapTh_plain = self.layers['elevation'].thresholds[1][1]
        p_world.heightMapTh_hill = self.layers['elevation'].thresholds[2][1]

        # Plates
        self._to_protobuf_matrix(self.layers['plates'].data, p_world.plates)

        # Ocean
        self._to_protobuf_matrix(self.layers['ocean'].data, p_world.ocean)
        self._to_protobuf_matrix(self.layers['sea_depth'].data, p_world.sea_depth)

        if self.has_biome():
            self._to_protobuf_matrix(self.layers['biome'].data, p_world.biome, biome_name_to_index)

        if self.has_humidity():
            self._to_protobuf_matrix_with_quantiles(self.layers['humidity'], p_world.humidity)

        if self.has_irrigation():
            self._to_protobuf_matrix(self.layers['irrigation'].data, p_world.irrigation)

        if self.has_permeability():
            self._to_protobuf_matrix(self.layers['permeability'].data,
                                     p_world.permeabilityData)
            p_world.permeability_low = self.layers['permeability'].thresholds[0][1]
            p_world.permeability_med = self.layers['permeability'].thresholds[1][1]

        if self.has_watermap():
            self._to_protobuf_matrix(self.layers['watermap'].data, p_world.watermapData)
            p_world.watermap_creek = self.layers['watermap'].thresholds['creek']
            p_world.watermap_river = self.layers['watermap'].thresholds['river']
            p_world.watermap_mainriver = self.layers['watermap'].thresholds['main river']

        if self.has_lakemap():
            self._to_protobuf_matrix(self.layers['lake_map'].data, p_world.lakemap)

        if self.has_rivermap():
            self._to_protobuf_matrix(self.layers['river_map'].data, p_world.rivermap)

        if self.has_precipitations():
            self._to_protobuf_matrix(self.layers['precipitation'].data, p_world.precipitationData)
            p_world.precipitation_low = self.layers['precipitation'].thresholds[0][1]
            p_world.precipitation_med = self.layers['precipitation'].thresholds[1][1]

        if self.has_temperature():
            self._to_protobuf_matrix(self.layers['temperature'].data, p_world.temperatureData)
            p_world.temperature_polar = self.layers['temperature'].thresholds[0][1]
            p_world.temperature_alpine = self.layers['temperature'].thresholds[1][1]
            p_world.temperature_boreal = self.layers['temperature'].thresholds[2][1]
            p_world.temperature_cool = self.layers['temperature'].thresholds[3][1]
            p_world.temperature_warm = self.layers['temperature'].thresholds[4][1]
            p_world.temperature_subtropical = self.layers['temperature'].thresholds[5][1]

        if self.has_icecap():
            self._to_protobuf_matrix(self.layers['icecap'].data, p_world.icecap)

        return p_world

    @classmethod
    def _from_protobuf_world(cls, p_world):
        w = World(p_world.name, Size(p_world.width, p_world.height),
                  p_world.generationData.seed,
                  GenerationParameters(p_world.generationData.n_plates,
                        p_world.generationData.ocean_level,
                        Step.get_by_name(p_world.generationData.step)))

        # Elevation
        e = numpy.array(World._from_protobuf_matrix(p_world.heightMapData))
        e_th = [('sea', p_world.heightMapTh_sea),
                ('plain', p_world.heightMapTh_plain),
                ('hill', p_world.heightMapTh_hill),
                ('mountain', None)]
        w.elevation = (e, e_th)

        # Plates
        w.plates = numpy.array(World._from_protobuf_matrix(p_world.plates))

        # Ocean
        w.ocean = numpy.array(World._from_protobuf_matrix(p_world.ocean))
        w.sea_depth = numpy.array(World._from_protobuf_matrix(p_world.sea_depth))

        # Biome
        if len(p_world.biome.rows) > 0:
            w.biome = numpy.array(World._from_protobuf_matrix(p_world.biome, biome_index_to_name), dtype=object)

        # Humidity
        if len(p_world.humidity.rows) > 0:
            w.humidity = World._from_protobuf_matrix_with_quantiles(p_world.humidity)

        if len(p_world.irrigation.rows) > 0:
            w.irrigation = numpy.array(World._from_protobuf_matrix(p_world.irrigation))

        if len(p_world.permeabilityData.rows) > 0:
            p = numpy.array(World._from_protobuf_matrix(p_world.permeabilityData))
            p_th = [
                ('low', p_world.permeability_low),
                ('med', p_world.permeability_med),
                ('hig', None)
            ]
            w.permeability = (p, p_th)

        if len(p_world.watermapData.rows) > 0:
            data = numpy.array(World._from_protobuf_matrix(
                p_world.watermapData))
            thresholds = {}
            thresholds['creek'] = p_world.watermap_creek
            thresholds['river'] = p_world.watermap_river
            thresholds['main river'] = p_world.watermap_mainriver
            w.watermap = (data, thresholds)

        if len(p_world.precipitationData.rows) > 0:
            p = numpy.array(World._from_protobuf_matrix(p_world.precipitationData))
            p_th = [
                ('low', p_world.precipitation_low),
                ('med', p_world.precipitation_med),
                ('hig', None)
            ]
            w.precipitation = (p, p_th)

        if len(p_world.temperatureData.rows) > 0:
            t = numpy.array(World._from_protobuf_matrix(p_world.temperatureData))
            t_th = [
                ('polar', p_world.temperature_polar),
                ('alpine', p_world.temperature_alpine),
                ('boreal', p_world.temperature_boreal),
                ('cool', p_world.temperature_cool),
                ('warm', p_world.temperature_warm),
                ('subtropical', p_world.temperature_subtropical),
                ('tropical', None)
            ]
            w.temperature = (t, t_th)

        if len(p_world.lakemap.rows) > 0:
            w.lakemap = numpy.array(World._from_protobuf_matrix(p_world.lakemap))

        if len(p_world.rivermap.rows) > 0:
            w.rivermap = numpy.array(World._from_protobuf_matrix(p_world.rivermap))

        if len(p_world.icecap.rows) > 0:
            w.icecap = numpy.array(World._from_protobuf_matrix(p_world.icecap))

        return w

    #
    # General
    #

    def contains(self, pos):
        return 0 <= pos[0] < self.width and 0 <= pos[1] < self.height

    #
    # Land/Ocean
    #

    def random_land(self, num_samples=1):
        if self.layers['ocean'].data.all():
            return None, None  # return invalid indices if there is no land at all

        land = numpy.invert(self.layers['ocean'].data)
        land_indices = numpy.transpose(numpy.nonzero(land))  # returns a list of tuples/indices with land positions

        result = numpy.zeros(num_samples*2, dtype=int)

        for i in range(0, num_samples*2, 2):
            r_num = numpy.random.randint(0, len(land_indices)) # uses global RNG
            result[i+1], result[i] = land_indices[r_num]

        return result

    def is_land(self, pos):
        return not self.layers['ocean'].data[pos[1], pos[0]]#faster than reversing pos or transposing ocean

    def is_ocean(self, pos):
        return self.layers['ocean'].data[pos[1], pos[0]]

    def sea_level(self):
        return self.layers['elevation'].thresholds[0][1]

    #
    # Tiles around
    #

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

    #
    # Elevation
    #

    def start_mountain_th(self):
        return self.layers['elevation'].thresholds[2][1]

    def get_mountain_level(self):
        if len(self.layers['elevation'].thresholds) == 4:
            mi = 2
        else:
            mi = 1
        return self.layers['elevation'].thresholds[mi][1]


    def is_mountain(self, pos):
        if self.is_ocean(pos):
            return False
        x, y = pos

        return self.layers['elevation'].data[y][x] > self.get_mountain_level()

    def is_low_mountain(self, pos):
        if not self.is_mountain(pos):
            return False
        if len(self.layers['elevation'].thresholds) == 4:
            mi = 2
        else:
            mi = 1
        mountain_level = self.layers['elevation'].thresholds[mi][1]
        x, y = pos
        return self.layers['elevation'].data[y, x] < mountain_level + 2.0

    def level_of_mountain(self, pos):
        mountain_level = self.get_mountain_level()
        x, y = pos
        if self.layers['elevation'].data[y, x] <= mountain_level:
            return 0
        else:
            return self.layers['elevation'].data[y, x] - mountain_level

    def is_high_mountain(self, pos):
        if not self.is_mountain(pos):
            return False
        if len(self.layers['elevation'].thresholds) == 4:
            mi = 2
        else:
            mi = 1
        mountain_level = self.layers['elevation'].thresholds[mi][1]
        x, y = pos
        return self.layers['elevation'].data[y, x] > mountain_level + 4.0

    def is_hill(self, pos):
        if self.is_ocean(pos):
            return False
        if len(self.layers['elevation'].thresholds) == 4:
            hi = 1
        else:
            hi = 0
        hill_level = self.layers['elevation'].thresholds[hi][1]
        mountain_level = self.layers['elevation'].thresholds[hi + 1][1]
        x, y = pos
        return hill_level < self.layers['elevation'].data[y, x] < mountain_level

    def elevation_at(self, pos):
        return self.layers['elevation'].data[pos[1], pos[0]]

    #
    # Precipitations
    #

    def precipitations_at(self, pos):
        x, y = pos
        return self.layers['precipitation'].data[y, x]

    def precipitations_thresholds(self):
        return self.layers['precipitation'].thresholds

    #
    # Temperature
    #

    def is_temperature_polar(self, pos):
        th_max = self.layers['temperature'].thresholds[0][1]
        x, y = pos
        t = self.layers['temperature'].data[y, x]
        return t < th_max

    def is_temperature_alpine(self, pos):
        th_min = self.layers['temperature'].thresholds[0][1]
        th_max = self.layers['temperature'].thresholds[1][1]
        x, y = pos
        t = self.layers['temperature'].data[y, x]
        return th_max > t >= th_min

    def is_temperature_boreal(self, pos):
        th_min = self.layers['temperature'].thresholds[1][1]
        th_max = self.layers['temperature'].thresholds[2][1]
        x, y = pos
        t = self.layers['temperature'].data[y, x]
        return th_max > t >= th_min

    def is_temperature_cool(self, pos):
        th_min = self.layers['temperature'].thresholds[2][1]
        th_max = self.layers['temperature'].thresholds[3][1]
        x, y = pos
        t = self.layers['temperature'].data[y, x]
        return th_max > t >= th_min

    def is_temperature_warm(self, pos):
        th_min = self.layers['temperature'].thresholds[3][1]
        th_max = self.layers['temperature'].thresholds[4][1]
        x, y = pos
        t = self.layers['temperature'].data[y, x]
        return th_max > t >= th_min

    def is_temperature_subtropical(self, pos):
        th_min = self.layers['temperature'].thresholds[4][1]
        th_max = self.layers['temperature'].thresholds[5][1]
        x, y = pos
        t = self.layers['temperature'].data[y, x]
        return th_max > t >= th_min

    def is_temperature_tropical(self, pos):
        th_min = self.layers['temperature'].thresholds[5][1]
        x, y = pos
        t = self.layers['temperature'].data[y, x]
        return t >= th_min

    def temperature_at(self, pos):
        x, y = pos
        return self.layers['temperature'].data[y, x]

    def temperature_thresholds(self):
        return self.layers['temperature'].thresholds

    #
    # Humidity
    #

    def humidity_at(self, pos):
        x, y = pos
        return self.layers['humidity'].data[y, x]

    def is_humidity_above_quantile(self, pos, q):
        th = self.layers['humidity'].quantiles[str(q)]
        x, y = pos
        t = self.layers['humidity'].data[y, x]
        return t >= th

    def is_humidity_superarid(self, pos):
        th_max = self.layers['humidity'].quantiles['87']
        x, y = pos
        t = self.layers['humidity'].data[y, x]
        return t < th_max

    def is_humidity_perarid(self, pos):
        th_min = self.layers['humidity'].quantiles['87']
        th_max = self.layers['humidity'].quantiles['75']
        x, y = pos
        t = self.layers['humidity'].data[y, x]
        return th_max > t >= th_min

    def is_humidity_arid(self, pos):
        th_min = self.layers['humidity'].quantiles['75']
        th_max = self.layers['humidity'].quantiles['62']
        x, y = pos
        t = self.layers['humidity'].data[y, x]
        return th_max > t >= th_min

    def is_humidity_semiarid(self, pos):
        th_min = self.layers['humidity'].quantiles['62']
        th_max = self.layers['humidity'].quantiles['50']
        x, y = pos
        t = self.layers['humidity'].data[y, x]
        return th_max > t >= th_min

    def is_humidity_subhumid(self, pos):
        th_min = self.layers['humidity'].quantiles['50']
        th_max = self.layers['humidity'].quantiles['37']
        x, y = pos
        t = self.layers['humidity'].data[y, x]
        return th_max > t >= th_min

    def is_humidity_humid(self, pos):
        th_min = self.layers['humidity'].quantiles['37']
        th_max = self.layers['humidity'].quantiles['25']
        x, y = pos
        t = self.layers['humidity'].data[y, x]
        return th_max > t >= th_min

    def is_humidity_perhumid(self, pos):
        th_min = self.layers['humidity'].quantiles['25']
        th_max = self.layers['humidity'].quantiles['12']
        x, y = pos
        t = self.layers['humidity'].data[y, x]
        return th_max > t >= th_min

    def is_humidity_superhumid(self, pos):
        th_min = self.layers['humidity'].quantiles['12']
        x, y = pos
        t = self.layers['humidity'].data[y, x]
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
        b = Biome.by_name(self.layers['biome'].data[y, x])
        if b is None:
            raise Exception('Not found')
        return b


    def is_iceland(self, pos):
        for subclass in Iceland.__subclasses__():
            if isinstance(self.biome_at(pos), subclass):
                return True

        return False


    #
    # Plates
    #

    def n_actual_plates(self):
        return self.layers['plates'].data.max() + 1

    #
    # Properties
    #

    @property
    def elevation(self):
        return self.layers['elevation'].data

    @elevation.setter
    def elevation(self, val):
        try:
            data, thresholds = val
        except ValueError:
            raise ValueError("Pass an iterable: (data, thresholds)")
        else:
            if data.shape != (self.height, self.width):
                raise Exception(
                    "Setting elevation map with wrong dimension. "
                    "Expected %d x %d, found %d x %d" % (
                        self.width, self.height, data.shape[1], data.shape[0]))
            self.layers['elevation'] = LayerWithThresholds(data, thresholds)

    @property
    def plates(self):
        return self.layers['plates'].data

    @plates.setter
    def plates(self, data):
        if (data.shape[0] != self.height) or (data.shape[1] != self.width):
            raise Exception(
                "Setting plates map with wrong dimension. "
                "Expected %d x %d, found %d x %d" % (
                    self.width, self.height, data.shape[1], data.shape[0]))
        self.layers['plates'] = Layer(data)

    @property
    def biome(self):
        return self.layers['biome'].data

    @biome.setter
    def biome(self, biome):
        if biome.shape[0] != self.height:
            raise Exception(
                "Setting data with wrong height: biome has height %i while "
                "the height is currently %i" % (
                    biome.shape[0], self.height))
        if biome.shape[1] != self.width:
            raise Exception("Setting data with wrong width")
        self.layers['biome'] = Layer(biome)

    @property
    def ocean(self):
        return self.layers['ocean'].data

    @ocean.setter
    def ocean(self, ocean):
        if (ocean.shape[0] != self.height) or (ocean.shape[1] != self.width):
            raise Exception(
                "Setting ocean map with wrong dimension. Expected %d x %d, "
                "found %d x %d" % (self.width, self.height,
                                   ocean.shape[1], ocean.shape[0]))
        self.layers['ocean'] = Layer(ocean)

    @property
    def sea_depth(self):
        return self.layers['sea_depth'].data

    @sea_depth.setter
    def sea_depth(self, data):
        if (data.shape[0] != self.height) or (data.shape[1] != self.width):
            raise Exception(
                "Setting sea depth map with wrong dimension. Expected %d x %d, "
                "found %d x %d" % (self.width, self.height,
                                   data.shape[1], data.shape[0]))
        self.layers['sea_depth'] = Layer(data)

    @property
    def precipitation(self):
        return self.layers['precipitation'].data

    @precipitation.setter
    def precipitation(self, val):
        """"Precipitation is a value in [-1,1]"""
        try:
            data, thresholds = val
        except ValueError:
            raise ValueError("Pass an iterable: (data, thresholds)")
        else:
            if data.shape[0] != self.height:
                raise Exception("Setting data with wrong height")
            if data.shape[1] != self.width:
                raise Exception("Setting data with wrong width")
            self.layers['precipitation'] = LayerWithThresholds(data, thresholds)

    @property
    def humidity(self):
        return self.layers['humidity'].data

    @humidity.setter
    def humidity(self, val):
        try:
            data, quantiles = val
            data = numpy.array(data)
        except ValueError:
            raise ValueError("Pass an iterable: (data, quantiles)")
        else:
            if data.shape[0] != self.height:
                raise Exception("Setting data with wrong height")
            if data.shape[1] != self.width:
                raise Exception("Setting data with wrong width")
            self.layers['humidity'] = LayerWithQuantiles(data, quantiles)

    @property
    def irrigation(self):
        return self.layers['irrigation'].data

    @irrigation.setter
    def irrigation(self, data):
        if data.shape[0] != self.height:
            raise Exception("Setting data with wrong height")
        if data.shape[1] != self.width:
            raise Exception("Setting data with wrong width")
        self.layers['irrigation'] = Layer(data)

    @property
    def temperature(self):
        return self.layers['temperature'].data

    @temperature.setter
    def temperature(self, val):
        try:
            data, thresholds = val
        except ValueError:
            raise ValueError("Pass an iterable: (data, thresholds)")
        else:
            if data.shape[0] != self.height:
                raise Exception("Setting data with wrong height")
            if data.shape[1] != self.width:
                raise Exception("Setting data with wrong width")
            self.layers['temperature'] = LayerWithThresholds(data, thresholds)

    @property
    def permeability(self):
        return self.layers['permeability'].data

    @permeability.setter
    def permeability(self, val):
        try:
            data, thresholds = val
        except ValueError:
            raise ValueError("Pass an iterable: (data, thresholds)")
        else:
            if data.shape[0] != self.height:
                raise Exception("Setting data with wrong height")
            if data.shape[1] != self.width:
                raise Exception("Setting data with wrong width")
            self.layers['permeability'] = LayerWithThresholds(data, thresholds)

    @property
    def watermap(self):
        return self.layers['watermap'].data

    @watermap.setter
    def watermap(self, val):
        try:
            data, thresholds = val
        except ValueError:
            raise ValueError("Pass an iterable: (data, thresholds)")
        else:
            if data.shape[0] != self.height:
                raise Exception("Setting data with wrong height")
            if data.shape[1] != self.width:
                raise Exception("Setting data with wrong width")
            self.layers['watermap'] = LayerWithThresholds(data, thresholds)

    @property
    def rivermap(self):
        return self.layers['river_map'].data

    @rivermap.setter
    def rivermap(self, river_map):
        self.layers['river_map'] = Layer(river_map)

    @property
    def lakemap(self):
        return self.layers['lake_map'].data

    @lakemap.setter
    def lakemap(self, lake_map):
        self.layers['lake_map'] = Layer(lake_map)

    @property
    def icecap(self):
        return self.layers['icecap'].data

    @icecap.setter
    def icecap(self, icecap):
        self.layers['icecap'] = Layer(icecap)

    #
    # Testers
    #

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
