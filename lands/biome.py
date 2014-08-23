__author__ = 'Federico Tomassetti'


class Biome:
    @classmethod
    def by_name(self, name):
        return BIOMES[name]

    def name(self):
        return str(type(self))


class Ocean(Biome):
    def name(self):
        return 'ocean'


class Sea(Biome):
    def name(self):
        return 'sea'


class Alpine(Biome):
    def name(self):
        return 'alpine'


class Glacier(Biome):
    def name(self):
        return 'glacier'


class Iceland(Biome):
    def name(self):
        return 'iceland'


class Steppe(Biome):
    def name(self):
        return 'steppe'


class Grassland(Biome):
    def name(self):
        return 'grassland'


class Jungle(Biome):
    def name(self):
        return 'jungle'


class Forest(Biome):
    def name(self):
        return 'forest'


class SandDesert(Biome):
    def name(self):
        return 'sand_desert'


class RockDesert(Biome):
    def name(self):
        return 'rock_desert'


class Savanna(Biome):
    def name(self):
        return 'savanna'


class Tundra(Biome):
    def name(self):
        return 'tundra'


class Swamp(Biome):
    def name(self):
        return 'swamp'


BIOMES = {
    'ocean': Ocean(),
    'sea': Sea(),
    'savanna': Savanna(),
    'alpine': Alpine(),
    'glacier': Glacier(),
    'iceland': Iceland(),
    'jungle': Jungle(),
    'rock desert': RockDesert(),
    'sand desert': SandDesert(),
    'steppe': Steppe(),
    'grassland': Grassland(),
    'forest': Forest(),
    'tundra': Tundra(),
    'swamp': Swamp()
}
