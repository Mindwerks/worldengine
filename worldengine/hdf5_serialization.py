import numpy

import h5py

from worldengine.version import __version__
from worldengine.biome import biome_name_to_index, biome_index_to_name
from worldengine.model.world import World, Step, Size, GenerationParameters


def save_world_to_hdf5(world, filename):
    f = h5py.File(filename, libver='latest', mode='w')

    general_grp = f.create_group("general")
    general_grp["worldengine_version"] = __version__
    general_grp["name"] = world.name
    general_grp["width"] = world.width
    general_grp["height"] = world.height

    elevation_grp = f.create_group("elevation")
    elevation_ths_grp = elevation_grp.create_group("thresholds")
    elevation_ths_grp["sea"] = world.layers['elevation'].thresholds[0][1]
    elevation_ths_grp["plain"] = world.layers['elevation'].thresholds[1][1]
    elevation_ths_grp["hill"] = world.layers['elevation'].thresholds[2][1]
    elevation_data = elevation_grp.create_dataset("data", (world.height, world.width), dtype=numpy.float)
    elevation_data.write_direct(world.layers['elevation'].data)

    plates_data = f.create_dataset("plates", (world.height, world.width), dtype=numpy.uint16)
    plates_data.write_direct(world.layers['plates'].data)

    ocean_data = f.create_dataset("ocean", (world.height, world.width), dtype=numpy.bool)
    ocean_data.write_direct(world.layers['ocean'].data)

    sea_depth_data = f.create_dataset("sea_depth", (world.height, world.width), dtype=numpy.float)
    sea_depth_data.write_direct(world.layers['sea_depth'].data)

    if world.has_biome():
        biome_data = f.create_dataset("biome", (world.height, world.width), dtype=numpy.uint16)
        for y in range(world.height):
            for x in range(world.width):
                biome_data[y, x] = biome_name_to_index(world.layers['biome'].data[y][x])

    if world.has_humidity():
        humidity_grp = f.create_group("humidity")
        humidity_quantiles_grp = humidity_grp.create_group("quantiles")
        for k in world.layers['humidity'].quantiles.keys():
            humidity_quantiles_grp[k] = world.layers['humidity'].quantiles[k]
        humidity_data = humidity_grp.create_dataset("data", (world.height, world.width), dtype=numpy.float)
        humidity_data.write_direct(world.layers['humidity'].data)

    if world.has_irrigation():
        irrigation_data = f.create_dataset("irrigation", (world.height, world.width), dtype=numpy.float)
        irrigation_data.write_direct(world.layers['irrigation'].data)

    if world.has_permeability():
        permeability_grp = f.create_group("permeability")
        permeability_ths_grp = permeability_grp.create_group("thresholds")
        permeability_ths_grp['low'] = world.layers['permeability'].thresholds[0][1]
        permeability_ths_grp['med'] = world.layers['permeability'].thresholds[1][1]
        permeability_data = permeability_grp.create_dataset("data", (world.height, world.width), dtype=numpy.float)
        permeability_data.write_direct(world.layers['permeability'].data)

    if world.has_watermap():
        watermap_grp = f.create_group("watermap")
        watermap_ths_grp = watermap_grp.create_group("thresholds")
        watermap_ths_grp['creek'] = world.layers['watermap'].thresholds['creek']
        watermap_ths_grp['river'] = world.layers['watermap'].thresholds['river']
        watermap_ths_grp['mainriver'] = world.layers['watermap'].thresholds['main river']
        watermap_data = watermap_grp.create_dataset("data", (world.height, world.width), dtype=numpy.float)
        watermap_data.write_direct(world.layers['watermap'].data)

    if world.has_precipitations():
        precipitation_grp = f.create_group("precipitation")
        precipitation_ths_grp = precipitation_grp.create_group("thresholds")
        precipitation_ths_grp['low'] = world.layers['precipitation'].thresholds[0][1]
        precipitation_ths_grp['med'] = world.layers['precipitation'].thresholds[1][1]
        precipitation_data = precipitation_grp.create_dataset("data", (world.height, world.width), dtype=numpy.float)
        precipitation_data.write_direct(world.layers['precipitation'].data)

    if world.has_temperature():
        temperature_grp = f.create_group("temperature")
        temperature_ths_grp = temperature_grp.create_group("thresholds")
        th = world.layers['temperature'].thresholds
        temperature_ths_grp['polar'] = th[0][1]
        temperature_ths_grp['alpine'] = th[1][1]
        temperature_ths_grp['boreal'] = th[2][1]
        temperature_ths_grp['cool'] = th[3][1]
        temperature_ths_grp['warm'] = th[4][1]
        temperature_ths_grp['subtropical'] = th[5][1]
        temperature_data = temperature_grp.create_dataset("data", (world.height, world.width), dtype=numpy.float)
        temperature_data.write_direct(world.layers['temperature'].data)

    if world.has_icecap():
        icecap_data = f.create_dataset("icecap", (world.height, world.width), dtype=numpy.float)
        icecap_data.write_direct(world.layers['icecap'].data)

    if world.has_lakemap():
        lake_map_data = f.create_dataset("lake_map", (world.height, world.width), dtype=numpy.float)
        lake_map_data.write_direct(world.layers['lake_map'].data)

    if world.has_rivermap():
        river_map_data = f.create_dataset("river_map", (world.height, world.width), dtype=numpy.float)
        river_map_data.write_direct(world.layers['river_map'].data)

    generation_params_grp = f.create_group("generation_params")
    generation_params_grp['seed'] = world.seed
    generation_params_grp['n_plates'] = world.n_plates
    generation_params_grp['ocean_level'] = world.ocean_level
    generation_params_grp['step'] = world.step.name

    f.close()


def _from_hdf5_quantiles(p_quantiles):
    quantiles = {}
    for p_quantile in p_quantiles:
        quantiles[p_quantile.title()] = p_quantiles[p_quantile].value
    return quantiles


def _from_hdf5_matrix_with_quantiles(p_matrix):
    return numpy.array(p_matrix['data']), _from_hdf5_quantiles(p_matrix['quantiles'])


def load_world_to_hdf5(filename):
    f = h5py.File(filename, libver='latest', mode='r')

    w = World(f['general/name'].value,
              Size(f['general/width'].value, f['general/height'].value),
              f['generation_params/seed'].value,
              GenerationParameters(f['generation_params/n_plates'].value,
                                   f['generation_params/ocean_level'].value,
                                   Step.get_by_name(f['generation_params/step'].value)))

    # Elevation
    e = numpy.array(f['elevation/data'])
    e_th = [('sea', f['elevation/thresholds/sea'].value),
            ('plain', f['elevation/thresholds/plain'].value),
            ('hill', f['elevation/thresholds/hill'].value),
            ('mountain', None)]
    w.set_elevation(e, e_th)

    # Plates
    w.set_plates(numpy.array(f['plates']))

    # Ocean
    w.set_ocean(numpy.array(f['ocean']))
    w.set_sea_depth(numpy.array(f['sea_depth']))

    # Biome
    if 'biome' in f.keys():
        biome_data = []
        for y in range(w.height):
            row = []
            for x in range(w.width):
                value = f['biome'][y, x]
                row.append(biome_index_to_name(value))
            biome_data.append(row)
        biome = numpy.array(biome_data, dtype=object)
        w.set_biome(biome)

    if 'humidity' in f.keys():
        data, quantiles = _from_hdf5_matrix_with_quantiles(f['humidity'])
        w.set_humidity(data, quantiles)

    if 'irrigation' in f.keys():
        w.set_irrigation(numpy.array(f['irrigation']))

    if 'permeability' in f.keys():
        p = numpy.array(f['permeability/data'])
        p_th = [
            ('low', f['permeability/thresholds/low'].value),
            ('med', f['permeability/thresholds/med'].value),
            ('hig', None)
        ]
        w.set_permeability(p, p_th)

    if 'watermap' in f.keys():
        data = numpy.array(f['watermap/data'])
        thresholds = {}
        thresholds['creek'] = f['watermap/thresholds/creek'].value
        thresholds['river'] =  f['watermap/thresholds/river'].value
        thresholds['main river'] = f['watermap/thresholds/mainriver'].value
        w.set_watermap(data, thresholds)

    if 'precipitation' in f.keys():
        p = numpy.array(f['precipitation/data'])
        p_th = [
            ('low', f['precipitation/thresholds/low'].value),
            ('med', f['precipitation/thresholds/med'].value),
            ('hig', None)
        ]
        w.set_precipitation(p, p_th)

    if 'temperature' in f.keys():
        t = numpy.array(f['temperature/data'])
        t_th = [
            ('polar', f['temperature/thresholds/polar'].value),
            ('alpine', f['temperature/thresholds/alpine'].value),
            ('boreal', f['temperature/thresholds/boreal'].value),
            ('cool', f['temperature/thresholds/cool'].value),
            ('warm', f['temperature/thresholds/warm'].value),
            ('subtropical', f['temperature/thresholds/subtropical'].value),
            ('tropical', None)
        ]
        w.set_temperature(t, t_th)

    if 'icecap' in f.keys():
        w.set_icecap(numpy.array(f['icecap']))

    if 'lake_map' in f.keys():
        m = numpy.array(f['lake_map'])
        w.set_lakemap(m)

    if 'river_map' in f.keys():
        m = numpy.array(f['river_map'])
        w.set_rivermap(m)

    f.close()

    return w