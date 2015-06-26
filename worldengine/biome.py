"""
This file contains all possible Biome as separate classes.
"""

import re


def _un_camelize(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1).lower()


class _BiomeMetaclass(type):

    def __new__(mcs, name, parents, dct):
        if not hasattr(_BiomeMetaclass, "biomes"):
            _BiomeMetaclass.biomes = {}
        un_camelized_name = _un_camelize(name)
        created_class = super(_BiomeMetaclass, mcs).__new__(mcs, name,
                                                            parents, dct)
        if object not in parents:
            _BiomeMetaclass.biomes[un_camelized_name] = created_class
        return created_class


class Biome(object):

    __metaclass__ = _BiomeMetaclass

    @classmethod
    def by_name(cls, name):
        if name not in _BiomeMetaclass.biomes:
            raise Exception("No biome named '%s'" % name)
        return _BiomeMetaclass.biomes[name]()

    @classmethod
    def all_names(cls):
        return _BiomeMetaclass.biomes.keys().sort()

    @classmethod
    def name(cls):
        return _un_camelize(cls.__name__)


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


# -------------
# Serialization
# -------------

def biome_name_to_index(biome_name):
    names = _BiomeMetaclass.biomes.keys()
    names.sort()
    for i in range(len(names)):
        if names[i] == biome_name:
            return i
    raise Exception("Not found")


def biome_index_to_name(biome_index):
    names = _BiomeMetaclass.biomes.keys()
    names.sort()
    if biome_index < 0 or biome_index >= len(names):
        raise Exception("Not found")
    return names[biome_index]
