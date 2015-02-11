"""
This file contains all possible Biome as separate classes.
"""
__author__ = 'Federico Tomassetti'

import re


def _uncamelize(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1).lower()


class BiomeMetaclass(type):

    def __new__(cls, name, parents, dct):
        if not hasattr(BiomeMetaclass, "biomes"):
            BiomeMetaclass.biomes = {}
        uncamelized_name = _uncamelize(name)
        print("%s -> %s" % (name, uncamelized_name))
        created_class = super(BiomeMetaclass, cls).__new__(cls, name, parents, dct)
        if object not in parents:
            BiomeMetaclass.biomes[uncamelized_name] = created_class
        return created_class


class Biome(object):

    __metaclass__ = BiomeMetaclass

    @classmethod
    def by_name(cls, name):
        if name not in BiomeMetaclass.biomes:
            raise Exception("No biome named '%s'" % name)
        return BiomeMetaclass.biomes[name]()

    @classmethod
    def name(cls):
        return _uncamelize(cls.__name__)


class Ocean(Biome):
    pass


class Sea(Biome):
    pass


class PolarDesert(Biome):
    pass


class Ice(Biome):
    pass


class SubpolarDryTundra(Biome):
    pass


class SubpolarMoistTundra(Biome):
    pass


class SubpolarWetTundra(Biome):
    pass


class SubpolarRainTundra(Biome):
    pass


class BorealDesert(Biome):
    pass


class BorealDryScrub(Biome):
    pass


class BorealMoistForest(Biome):
    pass


class BorealWetForest(Biome):
    pass


class BorealRainForest(Biome):
    pass

class CoolTemperateDesert(Biome):
    pass


class CoolTemperateDesertScrub(Biome):
    pass


class CoolTemperateSteppe(Biome):
    pass


class CoolTemperateMoistForest(Biome):
    pass


class CoolTemperateWetForest(Biome):
    pass


class CoolTemperateRainForest(Biome):
    pass


class WarmTemperateDesert(Biome):
    pass


class WarmTemperateDesertScrub(Biome):
    pass


class WarmTemperateThornScrub(Biome):
    pass


class WarmTemperateDryForest(Biome):
    pass


class WarmTemperateMoistForest(Biome):
    pass


class WarmTemperateWetForest(Biome):
    pass


class WarmTemperateRainForest(Biome):
    pass


class SubtropicalDesert(Biome):
    pass


class SubtropicalDesertScrub(Biome):
    pass


class SubtropicalThornWoodland(Biome):
    pass


class SubtropicalDryForest(Biome):
    pass


class SubtropicalMoistForest(Biome):
    pass


class SubtropicalWetForest(Biome):
    pass


class SubtropicalRainForest(Biome):
    pass


class TropicalDesert(Biome):
    pass


class TropicalDesertScrub(Biome):
    pass


class TropicalThornWoodland(Biome):
    pass


class TropicalVeryDryForest(Biome):
    pass


class TropicalDryForest(Biome):
    pass


class TropicalMoistForest(Biome):
    pass


class TropicalWetForest(Biome):
    pass


class TropicalRainForest(Biome):
    pass


def biome_name_to_index(biome_name):
    names = BiomeMetaclass.biomes.keys()
    names.sort()
    for i in xrange(len(names)):
        if names[i] == biome_name:
            return i
    raise Exception("Not found")


def biome_index_to_name(biome_index):
    names = BiomeMetaclass.biomes.keys()
    names.sort()
    return names[biome_index]
