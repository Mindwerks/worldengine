import worldengine.protobuf.World_pb2 as Protobuf
from worldengine.step import Step
from worldengine.model.world import World, Size, GenerationParameters
import numpy
from worldengine.biome import biome_name_to_index, biome_index_to_name


def protobuf_serialize(world):
    p_world = _to_protobuf_world(world)
    return p_world.SerializeToString()


def protobuf_to_file(world, filename):
    with open(filename, "wb") as f:
        f.write(protobuf_serialize(world))


def open_protobuf(filename):
    with open(filename, "rb") as f:
        content = f.read()
        return protobuf_unserialize(content)


def protobuf_unserialize(serialized):
    p_world = Protobuf.World()
    p_world.ParseFromString(serialized)
    return _from_protobuf_world(p_world)


def _to_protobuf_matrix(matrix, p_matrix, transformation=None):
    for row in matrix:
        p_row = p_matrix.rows.add()
        for cell in row:
            '''
            When using numpy, certain primitive types are replaced with
            numpy-specifc versions that, even though mostly compatible,
            cannot be digested by protobuf. This might change at some point;
            for now a conversion is necessary.
            '''
            if type(cell) is numpy.bool_:
                value = bool(cell)
            elif type(cell) is numpy.uint16:
                value = int(cell)
            else:
                value = cell
            if transformation:
                value = transformation(value)
            p_row.cells.append(value)


def _to_protobuf_quantiles(quantiles, p_quantiles):
    for k in quantiles:
        entry = p_quantiles.add()
        v = quantiles[k]
        entry.key = int(k)
        entry.value = v


def _to_protobuf_matrix_with_quantiles(matrix, p_matrix):
    _to_protobuf_quantiles(matrix.quantiles, p_matrix.quantiles)
    _to_protobuf_matrix(matrix.data, p_matrix)


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


def _from_protobuf_quantiles(p_quantiles):
    quantiles = {}
    for p_quantile in p_quantiles:
        quantiles[str(p_quantile.key)] = p_quantile.value
    return quantiles


def _from_protobuf_matrix_with_quantiles(p_matrix):
    data = _from_protobuf_matrix(p_matrix)
    quantiles = _from_protobuf_quantiles(p_matrix.quantiles)
    return data, quantiles


def _to_protobuf_world(world):
    p_world = Protobuf.World()

    p_world.worldengine_tag = World.worldengine_tag()
    p_world.worldengine_version = world.__version_hashcode__()

    p_world.name = world.name
    p_world.width = world.width
    p_world.height = world.height

    p_world.generationData.seed = world.seed
    p_world.generationData.n_plates = world.n_plates
    p_world.generationData.ocean_level = world.ocean_level
    p_world.generationData.step = world.step.name

    # Elevation
    _to_protobuf_matrix(world.elevation.data, p_world.heightMapData)
    p_world.heightMapTh_sea = world.elevation.thresholds[0][1]
    p_world.heightMapTh_plain = world.elevation.thresholds[1][1]
    p_world.heightMapTh_hill = world.elevation.thresholds[2][1]

    # Plates
    _to_protobuf_matrix(world.plates.data, p_world.plates)

    # Ocean
    _to_protobuf_matrix(world.ocean.data, p_world.ocean)
    _to_protobuf_matrix(world.sea_depth.data, p_world.sea_depth)

    if world.has_biome():
        _to_protobuf_matrix(world.biome.data, p_world.biome, biome_name_to_index)

    if world.has_humidity():
        _to_protobuf_matrix_with_quantiles(world.humidity, p_world.humidity)

    if world.has_irrigation():
        _to_protobuf_matrix(world.irrigation.data, p_world.irrigation)

    if world.has_permeability():
        _to_protobuf_matrix(world.permeability.data,p_world.permeabilityData)
        p_world.permeability_low = world.permeability.thresholds[0][1]
        p_world.permeability_med = world.permeability.thresholds[1][1]

    if world.has_watermap():
        _to_protobuf_matrix(world.watermap.data, p_world.watermapData)
        p_world.watermap_creek = world.watermap.thresholds['creek']
        p_world.watermap_river = world.watermap.thresholds['river']
        p_world.watermap_mainriver = world.watermap.thresholds['main river']

    if world.has_lakemap():
        _to_protobuf_matrix(world.lake_map.data, p_world.lakemap)

    if world.has_rivermap():
        _to_protobuf_matrix(world.river_map.data, p_world.rivermap)

    if world.has_precipitations():
        _to_protobuf_matrix(world.precipitation.data, p_world.precipitationData)
        p_world.precipitation_low = world.precipitation.thresholds[0][1]
        p_world.precipitation_med = world.precipitation.thresholds[1][1]

    if world.has_temperature():
        _to_protobuf_matrix(world.temperature.data, p_world.temperatureData)
        p_world.temperature_polar = world.temperature.thresholds[0][1]
        p_world.temperature_alpine = world.temperature.thresholds[1][1]
        p_world.temperature_boreal = world.temperature.thresholds[2][1]
        p_world.temperature_cool = world.temperature.thresholds[3][1]
        p_world.temperature_warm = world.temperature.thresholds[4][1]
        p_world.temperature_subtropical = world.temperature.thresholds[5][1]

    if world.has_icecap():
        _to_protobuf_matrix(world.icecap.data, p_world.icecap)

    return p_world


def _from_protobuf_world(p_world):
    w = World(p_world.name, Size(p_world.width, p_world.height),
              p_world.generationData.seed,
              GenerationParameters(p_world.generationData.n_plates,
                    p_world.generationData.ocean_level,
                    Step.get_by_name(p_world.generationData.step)))

    # Elevation
    e = numpy.array(_from_protobuf_matrix(p_world.heightMapData))
    e_th = [('sea', p_world.heightMapTh_sea),
            ('plain', p_world.heightMapTh_plain),
            ('hill', p_world.heightMapTh_hill),
            ('mountain', None)]
    w.set_elevation(e, e_th)

    # Plates
    w.set_plates(numpy.array(_from_protobuf_matrix(p_world.plates)))

    # Ocean
    w.set_ocean(numpy.array(_from_protobuf_matrix(p_world.ocean)))
    w.set_sea_depth(numpy.array(_from_protobuf_matrix(p_world.sea_depth)))

    # Biome
    if len(p_world.biome.rows) > 0:
        w.set_biome(numpy.array(_from_protobuf_matrix(p_world.biome, biome_index_to_name), dtype=object))

    # Humidity
    # FIXME: use setters
    if len(p_world.humidity.rows) > 0:
        data, quantiles = _from_protobuf_matrix_with_quantiles(p_world.humidity)
        w.set_humidity(numpy.array(data), quantiles)

    if len(p_world.irrigation.rows) > 0:
        w.set_irrigation(numpy.array(_from_protobuf_matrix(p_world.irrigation)))

    if len(p_world.permeabilityData.rows) > 0:
        p = numpy.array(_from_protobuf_matrix(p_world.permeabilityData))
        p_th = [
            ('low', p_world.permeability_low),
            ('med', p_world.permeability_med),
            ('hig', None)
        ]
        w.set_permeability(p, p_th)

    if len(p_world.watermapData.rows) > 0:
        data = numpy.array(_from_protobuf_matrix(
            p_world.watermapData))
        thresholds = {}
        thresholds['creek'] = p_world.watermap_creek
        thresholds['river'] = p_world.watermap_river
        thresholds['main river'] = p_world.watermap_mainriver
        w.set_watermap(data, thresholds)

    if len(p_world.precipitationData.rows) > 0:
        p = numpy.array(_from_protobuf_matrix(p_world.precipitationData))
        p_th = [
            ('low', p_world.precipitation_low),
            ('med', p_world.precipitation_med),
            ('hig', None)
        ]
        w.set_precipitation(p, p_th)

    if len(p_world.temperatureData.rows) > 0:
        t = numpy.array(_from_protobuf_matrix(p_world.temperatureData))
        t_th = [
            ('polar', p_world.temperature_polar),
            ('alpine', p_world.temperature_alpine),
            ('boreal', p_world.temperature_boreal),
            ('cool', p_world.temperature_cool),
            ('warm', p_world.temperature_warm),
            ('subtropical', p_world.temperature_subtropical),
            ('tropical', None)
        ]
        w.set_temperature(t, t_th)

    if len(p_world.lakemap.rows) > 0:
        m = numpy.array(_from_protobuf_matrix(p_world.lakemap))
        w.set_lakemap(m)

    if len(p_world.rivermap.rows) > 0:
        m = numpy.array(_from_protobuf_matrix(p_world.rivermap))
        w.set_rivermap(m)

    if len(p_world.icecap.rows) > 0:
        w.set_icecap(numpy.array(_from_protobuf_matrix(p_world.icecap)))

    return w