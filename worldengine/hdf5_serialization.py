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
    elevation_data = elevation_grp.create_dataset("data", (world.width, world.height), dtype='float')
    for y in range(world.height):
        for x in range(world.width):
            elevation_data[x, y] = world.elevation['data'][y][x]

    plates_data = f.create_dataset("plates", (world.width, world.height), dtype='int')
    for y in range(world.height):
        for x in range(world.width):
            plates_data[x, y] = world.plates[y][x]

    ocean_data = f.create_dataset("ocean", (world.width, world.height), dtype='bool')
    for y in range(world.height):
        for x in range(world.width):
            ocean_data[x, y] = world.ocean[y][x]

    sea_depth_data = f.create_dataset("sea_depth", (world.width, world.height), dtype='float')
    for y in range(world.height):
        for x in range(world.width):
            sea_depth_data[x, y] = world.sea_depth[y][x]

    if hasattr(world, 'biome'):
        biome_data = f.create_dataset("biome", (world.width, world.height), dtype='int')
        for y in range(world.height):
            for x in range(world.width):
                biome_data[x, y] = biome_name_to_index(world.biome[y][x])

    if hasattr(world, 'humidity'):
        humidity_grp = f.create_group("humidity")
        humidity_quantiles_grp = humidity_grp.create_group("quantiles")
        for k in world.humidity['quantiles'].keys():
            humidity_quantiles_grp[k] = world.humidity['quantiles'][k]
        humidity_data = humidity_grp.create_dataset("data", (world.width, world.height), dtype='float')
        for y in range(world.height):
            for x in range(world.width):
                humidity_data[x, y] = world.humidity['data'][y][x]

    if hasattr(world, 'irrigation'):
        irrigation_data = f.create_dataset("irrigation", (world.width, world.height), dtype='float')
        for y in range(world.height):
            for x in range(world.width):
                irrigation_data[x, y] = world.irrigation[y][x]

    generation_params_grp = f.create_group("generation_params")

    f.close()