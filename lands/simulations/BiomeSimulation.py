__author__ = 'Federico Tomassetti'


class BiomeSimulation(object):

    def is_applicable(self, world):
        return world.has_humidity() and world.has_temperature() and (not world.has_biome())

    def execute(self, world, seed):
        w = world
        width = world.width
        height = world.height
        ocean = world.ocean
        cm = {}
        biome_cm = {}
        biome = [[None for x in xrange(width)] for y in xrange(height)]
        for y in xrange(height):
            for x in xrange(width):
                if ocean[y][x]:
                    biome[y][x] = 'ocean'
                else:
                    if w.is_temperature_polar((x, y)):
                        if w.is_humidity_superarid((x, y)):
                            biome[y][x] = 'polar desert'
                        else:
                            biome[y][x] = 'ice'
                    elif w.is_temperature_alpine((x, y)):
                        if w.is_humidity_superarid((x, y)):
                            biome[y][x] = 'subpolar dry tundra'
                        elif w.is_humidity_perarid((x, y)):
                            biome[y][x] = 'subpolar moist tundra'
                        elif w.is_humidity_arid((x, y)):
                            biome[y][x] = 'subpolar wet tundra'
                        else:
                            biome[y][x] = 'subpolar rain tundra'
                    elif w.is_temperature_boreal((x, y)):
                        if w.is_humidity_superarid((x, y)):
                            biome[y][x] = 'boreal desert'
                        elif w.is_humidity_perarid((x, y)):
                            biome[y][x] = 'boreal dry scrub'
                        elif w.is_humidity_arid((x, y)):
                            biome[y][x] = 'boreal moist forest'
                        elif w.is_humidity_semiarid((x, y)):
                            biome[y][x] = 'boreal wet forest'
                        else:
                            biome[y][x] = 'boreal rain forest'
                    elif w.is_temperature_cool((x, y)):
                        if w.is_humidity_superarid((x, y)):
                            biome[y][x] = 'cool temperate desert'
                        elif w.is_humidity_perarid((x, y)):
                            biome[y][x] = 'cool temperate desert scrub'
                        elif w.is_humidity_arid((x, y)):
                            biome[y][x] = 'cool temperate steppe'
                        elif w.is_humidity_semiarid((x, y)):
                            biome[y][x] = 'cool temperate moist forest'
                        elif w.is_humidity_subhumid((x, y)):
                            biome[y][x] = 'cool temperate wet forest'
                        else:
                            biome[y][x] = 'cool temperate rain forest'
                    elif w.is_temperature_warm((x, y)):
                        if w.is_humidity_superarid((x, y)):
                            biome[y][x] = 'warm temperate desert'
                        elif w.is_humidity_perarid((x, y)):
                            biome[y][x] = 'warm temperate desert scrub'
                        elif w.is_humidity_arid((x, y)):
                            biome[y][x] = 'warm temperate thorn scrub'
                        elif w.is_humidity_semiarid((x, y)):
                            biome[y][x] = 'warm temperate dry forest'
                        elif w.is_humidity_subhumid((x, y)):
                            biome[y][x] = 'warm temperate moist forest'
                        elif w.is_humidity_humid((x, y)):
                            biome[y][x] = 'warm temperate wet forest'
                        else:
                            biome[y][x] = 'warm temperate rain forest'
                    elif w.is_temperature_subtropical((x, y)):
                        if w.is_humidity_superarid((x, y)):
                            biome[y][x] = 'subtropical desert'
                        elif w.is_humidity_perarid((x, y)):
                            biome[y][x] = 'subtropical desert scrub'
                        elif w.is_humidity_arid((x, y)):
                            biome[y][x] = 'subtropical thorn woodland'
                        elif w.is_humidity_semiarid((x, y)):
                            biome[y][x] = 'subtropical dry forest'
                        elif w.is_humidity_subhumid((x, y)):
                            biome[y][x] = 'subtropical moist forest'
                        elif w.is_humidity_humid((x, y)):
                            biome[y][x] = 'subtropical wet forest'
                        else:
                            biome[y][x] = 'subtropical rain forest'
                    elif w.is_temperature_tropical((x, y)):
                        if w.is_humidity_superarid((x, y)):
                            biome[y][x] = 'tropical desert'
                        elif w.is_humidity_perarid((x, y)):
                            biome[y][x] = 'tropical desert scrub'
                        elif w.is_humidity_arid((x, y)):
                            biome[y][x] = 'tropical thorn woodland'
                        elif w.is_humidity_semiarid((x, y)):
                            biome[y][x] = 'tropical very dry forest'
                        elif w.is_humidity_subhumid((x, y)):
                            biome[y][x] = 'tropical dry forest'
                        elif w.is_humidity_humid((x, y)):
                            biome[y][x] = 'tropical moist forest'
                        elif w.is_humidity_perhumid((x, y)):
                            biome[y][x] = 'tropical wet forest'
                        else:
                            biome[y][x] = 'tropical rain forest'
                    else:
                        biome[y][x] = 'bare rock'
                if not biome[y][x] in biome_cm:
                    biome_cm[biome[y][x]] = 0
                biome_cm[biome[y][x]] += 1
        w.set_biome(biome)
        return (cm, biome_cm)
