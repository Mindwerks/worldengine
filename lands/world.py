__author__ = 'Federico Tomassetti'

from lands.biome import *
from lands.basic_map_operations import *
import pickle
import lands.protobuf.World_pb2 as Protobuf

class World(object):
    """A world composed by name, dimensions and all the characteristics of each cell.
    """

    def __init__(self, name, width, height):
        self.name = name
        self.width = width
        self.height = height

    ###
    ### General methods
    ###

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    ###
    ### Serialization/Unserialization
    ###

    @classmethod
    def from_pickle_file(cls, filename):
        with open(filename, "rb") as f:
            return pickle.load(f)

    @classmethod
    def from_dict(cls, dict):
        instance = World(dict['name'], dict['width'], dict['height'])
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
    def _to_protobuf_matrix(matrix, p_matrix, transformation = None):
        for row in matrix:
            p_row = p_matrix.rows.add()
            for cell in row:
                value = cell
                if transformation:
                    value = transformation(value)
                p_row.cells.append(value)

    @staticmethod
    def _to_protobuf_quantiles(quantiles, p_quantiles):
        for k in quantiles:
            entry = p_quantiles.add()
            v = quantiles[k]
            entry.key   = int(k)
            entry.value = v   

    @staticmethod
    def _to_protobuf_matrix_with_quantiles(matrix, p_matrix):
        World._to_protobuf_quantiles(matrix['quantiles'], p_matrix.quantiles)
        World._to_protobuf_matrix(matrix['data'], p_matrix)                    

    @staticmethod
    def _from_protobuf_matrix(p_matrix, transformation = None):
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
        matrix = {}
        matrix['data'] = World._from_protobuf_matrix(p_matrix)
        matrix['quantiles'] = World._from_protobuf_quantiles(p_matrix.quantiles)
        return matrix


    def _to_protobuf_world(self):
        p_world = Protobuf.World()
        p_world.name   = self.name
        p_world.width  = self.width
        p_world.height = self.height

        # Elevation
        self._to_protobuf_matrix(self.elevation['data'], p_world.heightMapData)
        p_world.heightMapTh_sea   = self.elevation['thresholds'][0][1];
        p_world.heightMapTh_plain = self.elevation['thresholds'][1][1];
        p_world.heightMapTh_hill  = self.elevation['thresholds'][2][1];

        # Plates
        self._to_protobuf_matrix(self.plates, p_world.plates)

        # Ocean                            
        self._to_protobuf_matrix(self.ocean, p_world.ocean)
        self._to_protobuf_matrix(self.sea_depth, p_world.sea_depth)

        # Biome
        if hasattr(self, 'biome'):
            self._to_protobuf_matrix(self.biome, p_world.biome, biome_name_to_index)

        # Humidty
        if hasattr(self, 'humidity'):
            self._to_protobuf_matrix_with_quantiles(self.humidity, p_world.humidity)

        if hasattr(self, 'irrigation'):
            self._to_protobuf_matrix(self.irrigation, p_world.irrigation)

        if hasattr(self, 'permeability'):
            self._to_protobuf_matrix(self.permeability['data'], p_world.permeabilityData)
            p_world.permeability_low = self.permeability['thresholds'][0][1]
            p_world.permeability_med = self.permeability['thresholds'][1][1]

        if hasattr(self, 'watermap'):
            self._to_protobuf_matrix(self.watermap['data'], p_world.watermapData)
            p_world.watermap_creek = self.watermap['thresholds']['creek']
            p_world.watermap_river = self.watermap['thresholds']['river']
            p_world.watermap_mainriver = self.watermap['thresholds']['main river']            

        if hasattr(self, 'precipitation'):
            self._to_protobuf_matrix(self.precipitation['data'], p_world.precipitationData)
            p_world.precipitation_low = self.precipitation['thresholds'][0][1]
            p_world.precipitation_med = self.precipitation['thresholds'][1][1]

        if hasattr(self, 'temperature'):
            self._to_protobuf_matrix(self.temperature['data'], p_world.temperatureData)
            p_world.temperature_polar       = self.temperature['thresholds'][0][1]
            p_world.temperature_alpine      = self.temperature['thresholds'][1][1]
            p_world.temperature_boreal      = self.temperature['thresholds'][2][1]
            p_world.temperature_cool        = self.temperature['thresholds'][3][1]
            p_world.temperature_warm        = self.temperature['thresholds'][4][1]
            p_world.temperature_subtropical = self.temperature['thresholds'][5][1]

        return p_world

    @classmethod
    def _from_protobuf_world(cls, p_world):
        w = World(p_world.name, p_world.width, p_world.height)

        # Elevation
        e = World._from_protobuf_matrix(p_world.heightMapData)
        e_th = [('sea',      p_world.heightMapTh_sea), 
                ('plain',    p_world.heightMapTh_plain), 
                ('hill',     p_world.heightMapTh_hill), 
                ('mountain', None)]
        w.set_elevation(e, e_th)

        # Plates
        w.set_plates( World._from_protobuf_matrix(p_world.plates) )

        # Ocean
        w.set_ocean(World._from_protobuf_matrix(p_world.ocean))
        w.sea_depth = World._from_protobuf_matrix(p_world.sea_depth)

        # Biome
        if len(p_world.biome.rows) > 0:
            w.set_biome(World._from_protobuf_matrix(p_world.biome, biome_index_to_name))

        # Humidity
        # FIXME: use setters
        if len(p_world.humidity.rows) > 0:
            w.humidity = World._from_protobuf_matrix_with_quantiles(p_world.humidity)

        if len(p_world.irrigation.rows) > 0:
            w.irrigation = World._from_protobuf_matrix(p_world.irrigation)

        if len(p_world.permeabilityData.rows) > 0:
            p = World._from_protobuf_matrix(p_world.permeabilityData)
            p_th = [
                ('low' , p_world.permeability_low),
                ('med' , p_world.permeability_med),
                ('hig' , None)
            ]
            w.set_permeability(p, p_th)

        if len(p_world.watermapData.rows) > 0:
            w.watermap = {}
            w.watermap['data'] = World._from_protobuf_matrix(p_world.watermapData)
            w.watermap['thresholds'] = {}
            w.watermap['thresholds']['creek'] = p_world.watermap_creek
            w.watermap['thresholds']['river'] = p_world.watermap_river
            w.watermap['thresholds']['main river'] = p_world.watermap_mainriver

        if len(p_world.precipitationData.rows) > 0:
            p = World._from_protobuf_matrix(p_world.precipitationData)
            p_th = [
                ('low' , p_world.precipitation_low),
                ('med' , p_world.precipitation_med),
                ('hig' , None)
            ]
            w.set_precipitation(p, p_th)

        if len(p_world.temperatureData.rows) > 0:
            t = World._from_protobuf_matrix(p_world.temperatureData)
            t_th = [
                ('polar',       p_world.temperature_polar),
                ('alpine',      p_world.temperature_alpine),
                ('boreal',      p_world.temperature_boreal),
                ('cool',        p_world.temperature_cool),
                ('warm',        p_world.temperature_warm),
                ('subtropical', p_world.temperature_subtropical),
                ('tropical',    None)
            ]
            w.set_temperature(t, t_th)

        return w

    ###
    ### Land/Ocean
    ###

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

    ###
    ### Tiles around
    ###

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


    ###
    ### Elevation
    ###

    def start_mountain_th(self):
        return self.elevation['thresholds'][2][1]

    def max_elevation(self):
        max_el = None
        for y in xrange(self.height):
            for x in xrange(self.width):
                el = self.elevation['data'][y][x]
                if max_el == None or el > max_el:
                    max_el = el
        return max_el

    def min_elevation(self):
        min_el = None
        for y in xrange(self.height):
            for x in xrange(self.width):
                el = self.elevation['data'][y][x]
                if min_el == None or el < min_el:
                    min_el = el
        return min_el        

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

    ###
    ### Temperature
    ###

    def is_temperature_polar(self, pos):
        th_max = self.temperature['thresholds'][0][1]
        x, y = pos
        t = self.temperature['data'][y][x]
        return t < th_max

    def is_temperature_alpine(self, pos):
        th_min = self.temperature['thresholds'][0][1]
        th_max = self.temperature['thresholds'][1][1]
        x, y = pos
        t = self.temperature['data'][y][x]
        return t < th_max and t >= th_min

    def is_temperature_boreal(self, pos):
        th_min = self.temperature['thresholds'][1][1]
        th_max = self.temperature['thresholds'][2][1]
        x, y = pos
        t = self.temperature['data'][y][x]
        return t < th_max and t >= th_min

    def is_temperature_cool(self, pos):
        th_min = self.temperature['thresholds'][2][1]
        th_max = self.temperature['thresholds'][3][1]
        x, y = pos
        t = self.temperature['data'][y][x]
        return t < th_max and t >= th_min

    def is_temperature_warm(self, pos):
        th_min = self.temperature['thresholds'][3][1]
        th_max = self.temperature['thresholds'][4][1]
        x, y = pos
        t = self.temperature['data'][y][x]
        return t < th_max and t >= th_min

    def is_temperature_subtropical(self, pos):
        th_min = self.temperature['thresholds'][4][1]
        th_max = self.temperature['thresholds'][5][1]
        x, y = pos
        t = self.temperature['data'][y][x]
        return t < th_max and t >= th_min

    def is_temperature_tropical(self, pos):
        th_min = self.temperature['thresholds'][5][1]
        x, y = pos
        t = self.temperature['data'][y][x]
        return t >= th_min

    ###
    ### Humidity
    ###

    def is_humidity_above_quantile(self, pos, q):
        th = self.humidity['quantiles'][str(q)]
        x, y = pos
        v = self.humidity['data'][y][x]
        return v >= th

    def is_humidity_superarid(self, pos):
        th_max = self.humidity['quantiles']['87']
        x, y = pos
        t = self.humidity['data'][y][x]
        return t < th_max

    def is_humidity_perarid(self, pos):
        th_min = self.humidity['quantiles']['87']
        th_max = self.humidity['quantiles']['75']
        x, y = pos
        t = self.humidity['data'][y][x]
        return t >= th_min and t < th_max

    def is_humidity_arid(self, pos):
        th_min = self.humidity['quantiles']['75']
        th_max = self.humidity['quantiles']['62']
        x, y = pos
        t = self.humidity['data'][y][x]
        return t >= th_min and t < th_max

    def is_humidity_semiarid(self, pos):
        th_min = self.humidity['quantiles']['62']
        th_max = self.humidity['quantiles']['50']
        x, y = pos
        t = self.humidity['data'][y][x]
        return t >= th_min and t < th_max

    def is_humidity_subhumid(self, pos):
        th_min = self.humidity['quantiles']['50']
        th_max = self.humidity['quantiles']['37']
        x, y = pos
        t = self.humidity['data'][y][x]
        return t >= th_min and t < th_max

    def is_humidity_humid(self, pos):
        th_min = self.humidity['quantiles']['37']
        th_max = self.humidity['quantiles']['25']
        x, y = pos
        t = self.humidity['data'][y][x]
        return t >= th_min and t < th_max

    def is_humidity_perhumid(self, pos):
        th_min = self.humidity['quantiles']['25']
        th_max = self.humidity['quantiles']['12']
        x, y = pos
        t = self.humidity['data'][y][x]
        return t >= th_min and t < th_max

    def is_humidity_superhumid(self, pos):
        th_min = self.humidity['quantiles']['12']
        x, y = pos
        t = self.humidity['data'][y][x]
        return t >= th_min

    ###
    ### Streams
    ###

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

    def watermap_at(self, pos):
        x, y = pos
        return self.watermap['data'][y][x]


    ###
    ### Biome
    ###

    def biome_at(self, pos):
        x, y = pos
        b = Biome.by_name(self.biome[y][x])
        if b == None:
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

    def is_glacier(self, pos):
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

    def is_rock_desert(self, pos):
        return False

    ###
    ### Plates
    ###

    def n_plates(self):
        res = -1
        for row in self.plates:
            for cell in row:
                res = max([cell, res])
        return res + 1

    ###
    ### Setters
    ###

    def set_elevation(self, data, thresholds):
        if (len(data) != self.height) or (len(data[0]) != self.width):
            raise Exception("Setting elevation map with wrong dimension. Expected %d x %d, found %d x %d" % (
                self.width, self.height, (len[data[0]], len(data))))
        self.elevation = {'data': data, 'thresholds': thresholds}


    def set_plates(self, data):
        if (len(data) != self.height) or (len(data[0]) != self.width):
            raise Exception("Setting plates map with wrong dimension. Expected %d x %d, found %d x %d" % (
                self.width, self.height, (len[data[0]], len(data))))
        self.plates = data

    def set_biome(self, biome):
        if len(biome) != self.height:
            raise Exception("Setting data with wrong height: biome has height %i while the height is currently %i" % (len(biome), self.height))
        if len(biome[0]) != self.width:
            raise Exception("Setting data with wrong width")

        self.biome = biome

    def set_ocean(self, ocean):
        if (len(ocean) != self.height) or (len(ocean[0]) != self.width):
            raise Exception("Setting ocean map with wrong dimension. Expected %d x %d, found %d x %d" % (
                self.width, self.height, len(ocean[0]), len(ocean)))

        self.ocean = ocean

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

    def has_precipitations(self):
        return hasattr(self, 'precipitation')

    def has_watermap(self):
        return hasattr(self, 'watermap')

    def has_irrigation(self):
        return hasattr(self, 'irrigation')

    def has_humidity(self):
        return hasattr(self, 'humidity')

    def has_temperature(self):
        return hasattr(self, 'temperature')

    def has_permeability(self):
        return hasattr(self, 'permeability')

    def has_biome(self):
        return hasattr(self, 'biome')
