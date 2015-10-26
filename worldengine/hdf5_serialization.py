import h5py
from worldengine.version import __version__
from worldengine.biome import biome_name_to_index


def save_hdf5(world, filename):
    f = h5py.File(filename, libver='latest', mode='w')

    general_grp = f.create_group("general")
    general_grp["worldengine_version"] = __version__
    general_grp["name"] = world.name
    general_grp["width"] = world.width
    general_grp["height"] = world.height

    elevation_grp = f.create_group("elevation")
    elevation_ths_grp = elevation_grp.create_group("thresholds")
    elevation_ths_grp["sea"] = world.elevation['thresholds'][0][1]
    elevation_ths_grp["plain"] = world.elevation['thresholds'][1][1]
    elevation_ths_grp["hill"] = world.elevation['thresholds'][2][1]
    elevation_data = elevation_grp.create_dataset("data", (world.height, world.width), dtype='float')
    for y in range(world.height):
        for x in range(world.width):
            elevation_data[y, x] = world.elevation['data'][y][x]

    plates_data = f.create_dataset("plates", (world.height, world.width), dtype='int')
    for y in range(world.height):
        for x in range(world.width):
            plates_data[y, x] = world.plates[y][x]

    ocean_data = f.create_dataset("ocean", (world.height, world.width), dtype='bool')
    for y in range(world.height):
        for x in range(world.width):
            ocean_data[y, x] = world.ocean[y][x]

    sea_depth_data = f.create_dataset("sea_depth", (world.height, world.width), dtype='float')
    for y in range(world.height):
        for x in range(world.width):
            sea_depth_data[y, x] = world.sea_depth[y][x]

    if hasattr(world, 'biome'):
        biome_data = f.create_dataset("biome", (world.height, world.width), dtype='int')
        for y in range(world.height):
            for x in range(world.width):
                biome_data[y, x] = biome_name_to_index(world.biome[y][x])

    if hasattr(world, 'humidity'):
        humidity_grp = f.create_group("humidity")
        humidity_quantiles_grp = humidity_grp.create_group("quantiles")
        for k in world.humidity['quantiles'].keys():
            humidity_quantiles_grp[k] = world.humidity['quantiles'][k]
        humidity_data = humidity_grp.create_dataset("data", (world.height, world.width), dtype='float')
        for y in range(world.height):
            for x in range(world.width):
                humidity_data[y, x] = world.humidity['data'][y][x]

    if hasattr(world, 'irrigation'):
        irrigation_data = f.create_dataset("irrigation", (world.height, world.width), dtype='float')
        for y in range(world.height):
            for x in range(world.width):
                irrigation_data[y, x] = world.irrigation[y][x]

    if hasattr(world, 'permeability'):
        permeability_grp = f.create_group("permeability")
        permeability_ths_grp = permeability_grp.create_group("thresholds")
        permeability_ths_grp['low'] = world.permeability['thresholds'][0][1]
        permeability_ths_grp['med'] = world.permeability['thresholds'][1][1]
        permeability_data = permeability_grp.create_dataset("data", (world.height, world.width), dtype='float')
        for y in range(world.height):
            for x in range(world.width):
                permeability_data[y, x] = world.permeability['data'][y][x]

    if hasattr(world, 'watermap'):
        watermap_grp = f.create_group("watermap")
        watermap_ths_grp = watermap_grp.create_group("thresholds")
        watermap_ths_grp['creek'] = world.watermap['thresholds']['creek']
        watermap_ths_grp['river'] = world.watermap['thresholds']['river']
        watermap_ths_grp['mainriver'] = world.watermap['thresholds']['main river']
        watermap_data = watermap_grp.create_dataset("data", (world.height, world.width), dtype='float')
        for y in range(world.height):
            for x in range(world.width):
                watermap_data[y, x] = world.watermap['data'][y][x]

    if hasattr(world, 'precipitation'):
        precipitation_grp = f.create_group("precipitation")
        precipitation_ths_grp = precipitation_grp.create_group("thresholds")
        precipitation_ths_grp['low'] = world.precipitation['thresholds'][0][1]
        precipitation_ths_grp['med'] = world.precipitation['thresholds'][1][1]
        precipitation_data = precipitation_grp.create_dataset("data", (world.height, world.width), dtype='float')
        for y in range(world.height):
            for x in range(world.width):
                precipitation_data[y, x] = world.precipitation['data'][y][x]

    if hasattr(world, 'temperature'):
        temperature_grp = f.create_group("temperature")
        temperature_ths_grp = temperature_grp.create_group("thresholds")
        temperature_ths_grp['polar'] = world.temperature['thresholds'][0][1]
        temperature_ths_grp['alpine'] = world.temperature['thresholds'][1][1]
        temperature_ths_grp['boreal'] = world.temperature['thresholds'][2][1]
        temperature_ths_grp['cool'] = world.temperature['thresholds'][3][1]
        temperature_ths_grp['warm'] = world.temperature['thresholds'][4][1]
        temperature_ths_grp['subtropical'] = world.temperature['thresholds'][5][1]
        temperature_data = temperature_grp.create_dataset("data", (world.height, world.width), dtype='float')
        for y in range(world.height):
            for x in range(world.width):
                temperature_data[y, x] = world.temperature['data'][y][x]

    if hasattr(world, 'lake_map'):
        lake_map_data = f.create_dataset("lake_map", (world.height, world.width), dtype='float')
        for y in range(world.height):
            for x in range(world.width):
                # lake_map and river_map have inverted coordinates
                lake_map_data[y, x] = world.lake_map[x][y]

    if hasattr(world, 'river_map'):
        river_map_data = f.create_dataset("river_map", (world.height, world.width), dtype='float')
        for y in range(world.height):
            for x in range(world.width):
                # lake_map and river_map have inverted coordinates
                river_map_data[y, x] = world.river_map[x][y]

    generation_params_grp = f.create_group("generation_params")
    generation_params_grp['seed'] = world.seed
    generation_params_grp['n_plates'] = world.n_plates
    generation_params_grp['ocean_level'] = world.ocean_level
    generation_params_grp['step'] = world.step.name

    f.close()