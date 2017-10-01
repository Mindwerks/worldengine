"""
This file contains all possible Biome as separate classes.
"""

import re
from six import with_metaclass


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


class Biome(with_metaclass(_BiomeMetaclass, object)):

    @classmethod
    def by_name(cls, name):
        if name not in _BiomeMetaclass.biomes:
            raise Exception("No biome named '%s'" % name)
        return _BiomeMetaclass.biomes[name]()

    @classmethod
    def all_names(cls):
        return sorted(_BiomeMetaclass.biomes.keys())

    @classmethod
    def name(cls):
        return _un_camelize(cls.__name__)

class BiomeGroup(object):
    pass


class BorealForest(BiomeGroup):
    pass


class CoolTemperateForest(BiomeGroup):
    pass


class WarmTemperateForest(BiomeGroup):
    pass


class TropicalDryForestGroup(BiomeGroup):
    pass


class Tundra(BiomeGroup):
    pass


class Iceland(BiomeGroup):
    pass


class Jungle(BiomeGroup):
    pass


class Savanna(BiomeGroup):
    pass


class HotDesert(BiomeGroup):
    pass


class ColdParklands(BiomeGroup):
    pass


class Steppe(BiomeGroup):
    pass


class CoolDesert(BiomeGroup):
    pass


class Chaparral(BiomeGroup):
    """ Chaparral is a shrubland or heathland plant community.

    For details see http://en.wikipedia.org/wiki/Chaparral.
    """
    pass


class Ocean(Biome):
    pass


class Sea(Biome):
    pass


class PolarDesert(Biome, Iceland):
    pass


class Ice(Biome, Iceland):
    pass


class SubpolarDryTundra(Biome, ColdParklands):
    pass


class SubpolarMoistTundra(Biome, Tundra):
    pass


class SubpolarWetTundra(Biome, Tundra):
    pass


class SubpolarRainTundra(Biome, Tundra):
    pass


class BorealDesert(Biome, ColdParklands):
    pass


class BorealDryScrub(Biome, ColdParklands):
    pass


class BorealMoistForest(Biome, BorealForest):
    pass


class BorealWetForest(Biome, BorealForest):
    pass


class BorealRainForest(Biome, BorealForest):
    pass


class CoolTemperateDesert(Biome, CoolDesert):
    pass


class CoolTemperateDesertScrub(Biome, CoolDesert):
    pass


class CoolTemperateSteppe(Biome, Steppe):
    pass


class CoolTemperateMoistForest(Biome, CoolTemperateForest):
    pass


class CoolTemperateWetForest(Biome, CoolTemperateForest):
    pass


class CoolTemperateRainForest(Biome, CoolTemperateForest):
    pass


class WarmTemperateDesert(Biome, HotDesert):
    pass


class WarmTemperateDesertScrub(Biome, HotDesert):
    pass


class WarmTemperateThornScrub(Biome, Chaparral):
    pass


class WarmTemperateDryForest(Biome, Chaparral):
    pass


class WarmTemperateMoistForest(Biome, WarmTemperateForest):
    pass


class WarmTemperateWetForest(Biome, WarmTemperateForest):
    pass


class WarmTemperateRainForest(Biome, WarmTemperateForest):
    pass


class SubtropicalDesert(Biome, HotDesert):
    pass


class SubtropicalDesertScrub(Biome, HotDesert):
    pass


class SubtropicalThornWoodland(Biome, Savanna):
    pass


class SubtropicalDryForest(Biome, TropicalDryForestGroup):
    pass


class SubtropicalMoistForest(Biome, Jungle):
    pass


class SubtropicalWetForest(Biome, Jungle):
    pass


class SubtropicalRainForest(Biome, Jungle):
    pass


class TropicalDesert(Biome, HotDesert):
    pass


class TropicalDesertScrub(Biome, HotDesert):
    pass


class TropicalThornWoodland(Biome, Savanna):
    pass


class TropicalVeryDryForest(Biome, Savanna):
    pass


class TropicalDryForest(Biome, TropicalDryForestGroup):
    pass


class TropicalMoistForest(Biome, Jungle):
    pass


class TropicalWetForest(Biome, Jungle):
    pass


class TropicalRainForest(Biome, Jungle):
    pass


# -------------
# Serialization
# -------------

def biome_name_to_index(biome_name):
    names = sorted(_BiomeMetaclass.biomes.keys())
    for i in range(len(names)):
        if names[i] == biome_name:
            return i
    raise Exception("Not found")


def biome_index_to_name(biome_index):
    names = sorted(_BiomeMetaclass.biomes.keys())
    if not 0 <= biome_index < len(names):
        raise Exception("Not found")
    return names[biome_index]
