"""
This file contains all possible Biome as separate classes.
"""
__author__ = 'Federico Tomassetti'


class Biome(object):
    @classmethod
    def by_name(cls, name):
        return BIOMES[name]

    def name(self):
        return str(type(self))


class Ocean(Biome):
    def name(self):
        return 'ocean'


class Sea(Biome):
    def name(self):
        return 'sea'


class PolarDesert(Biome):
    def name(self):
        return 'polar desert'


class Ice(Biome):
    def name(self):
        return 'ice'


class SubpolarDryTundra(Biome):
    def name(self):
        return 'subpolar dry tundra'


class SubpolarMoistTundra(Biome):
    def name(self):
        return 'subpolar moist tundra'


class SubpolarWetTundra(Biome):
    def name(self):
        return 'subpolar wet tundra'


class SubpolarRainTundra(Biome):
    def name(self):
        return 'subpolar rain tundra'


class BorealDesert(Biome):
    def name(self):
        return 'boreal desert'


class BorealDryScrub(Biome):
    def name(self):
        return 'boreal dry scrub'


class BorealMoistForest(Biome):
    def name(self):
        return 'boreal moist forest'


class BorealWetForest(Biome):
    def name(self):
        return 'boreal wet forest'


class BorealRainForest(Biome):
    def name(self):
        return 'boreal rain forest'


class CoolTemperateDesert(Biome):
    def name(self):
        return 'cool temperate desert'


class CoolTemperateDesertScrub(Biome):
    def name(self):
        return 'cool temperate desert scrub'


class CoolTemperateSteppe(Biome):
    def name(self):
        return 'cool temperate steepe'


class CoolTemperateMoistForest(Biome):
    def name(self):
        return 'cool temperate moist forest'


class CoolTemperateWetForest(Biome):
    def name(self):
        return 'cool temperate wet forest'


class CoolTemperateRainForest(Biome):
    def name(self):
        return 'cool temperate rain forest'


class WarmTemperateDesert(Biome):
    def name(self):
        return 'warm temperate desert'


class WarmTemperateDesertScrub(Biome):
    def name(self):
        return 'warm temperate desert scrub'


class WarmTemperateThornScrub(Biome):
    def name(self):
        return 'warm temperate thorn scrub'


class WarmTemperateDryForest(Biome):
    def name(self):
        return 'warm temperate dry forest'


class WarmTemperateMoistForest(Biome):
    def name(self):
        return 'warm temperate moist forest'


class WarmTemperateWetForest(Biome):
    def name(self):
        return 'warm temperate wet forest'


class WarmTemperateRainForest(Biome):
    def name(self):
        return 'warm temperate rain forest'


class SubtropicalDesert(Biome):
    def name(self):
        return 'subtropical desert'


class SubtropicalDesertScrub(Biome):
    def name(self):
        return 'subtropical desert scrub'


class SubtropicalThornWoodland(Biome):
    def name(self):
        return 'subtropical thorn woodland'


class SubtropicalDryForest(Biome):
    def name(self):
        return 'subtropical dry forest'


class SubtropicalMoistForest(Biome):
    def name(self):
        return 'subtropical moist forest'


class SubtropicalWetForest(Biome):
    def name(self):
        return 'subtropical wet forest'


class SubtropicalRainForest(Biome):
    def name(self):
        return 'subtropical rain forest'


class TropicalDesert(Biome):
    def name(self):
        return 'tropical desert'


class TropicalDesertScrub(Biome):
    def name(self):
        return 'tropical desert scrub'


class TropicalThornWoodland(Biome):
    def name(self):
        return 'tropical thorn woodland'


class TropicalVeryDryForest(Biome):
    def name(self):
        return 'tropical very dry forest'


class TropicalDryForest(Biome):
    def name(self):
        return 'tropical dry forest'


class TropicalMoistForest(Biome):
    def name(self):
        return 'tropical moist forest'


class TropicalWetForest(Biome):
    def name(self):
        return 'tropical wet forest'


class TropicalRainForest(Biome):
    def name(self):
        return 'tropical rain forest'


def biome_name_to_index(biome_name):
    names = BIOMES.keys()
    names.sort()
    for i in xrange(len(names)):
        if names[i] == biome_name:
            return i
    raise Exception("Not found")


def biome_index_to_name(biome_index):
    names = BIOMES.keys()
    names.sort()
    return names[biome_index]

BIOMES = {
    'ocean': Ocean(),
    'polar desert': PolarDesert(),
    'ice': Ice(),
    'subpolar dry tundra': SubpolarDryTundra(),
    'subpolar moist tundra': SubpolarMoistTundra(),
    'subpolar wet tundra': SubpolarWetTundra(),
    'subpolar rain tundra': SubpolarRainTundra(),
    'boreal desert': BorealDesert(),
    'boreal dry scrub': BorealDryScrub(),
    'boreal moist forest': BorealMoistForest(),
    'boreal wet forest': BorealWetForest(),
    'boreal rain forest': BorealRainForest(),
    'cool temperate desert': CoolTemperateDesert(),
    'cool temperate desert scrub': CoolTemperateDesertScrub(),
    'cool temperate steppe': CoolTemperateSteppe(),
    'cool temperate moist forest': CoolTemperateMoistForest(),
    'cool temperate wet forest': CoolTemperateWetForest(),
    'cool temperate rain forest': CoolTemperateRainForest(),
    'warm temperate desert': WarmTemperateDesert(),
    'warm temperate desert scrub': WarmTemperateDesertScrub(),
    'warm temperate thorn scrub': WarmTemperateThornScrub(),
    'warm temperate dry forest': WarmTemperateDryForest(),
    'warm temperate moist forest': WarmTemperateMoistForest(),
    'warm temperate wet forest': WarmTemperateWetForest(),
    'warm temperate rain forest': WarmTemperateRainForest(),
    'subtropical desert': SubtropicalDesert(),
    'subtropical desert scrub': SubtropicalDesertScrub(),
    'subtropical thorn woodland': SubtropicalThornWoodland(),
    'subtropical dry forest': SubtropicalDryForest(),
    'subtropical moist forest': SubtropicalMoistForest(),
    'subtropical wet forest': SubtropicalWetForest(),
    'subtropical rain forest': SubtropicalRainForest(),
    'tropical desert': TropicalDesert(),
    'tropical desert scrub': TropicalDesertScrub(),
    'tropical thorn woodland': TropicalThornWoodland(),
    'tropical very dry forest': TropicalVeryDryForest(),
    'tropical dry forest': TropicalDryForest(),
    'tropical moist forest': TropicalMoistForest(),
    'tropical wet forest': TropicalWetForest(),
    'tropical rain forest': TropicalRainForest(),
}
