__author__ = 'Federico Tomassetti'


class Biome:
    @classmethod
    def by_name(self, name):
        return BIOMES[name]

    def name(self):
        return str(type(self))


class Ocean(Biome):
    def __init__(self):
        self.sustainable_population = 250

    def name(self):
        return 'ocean'


class Sea(Biome):
    def __init__(self):
        self.sustainable_population = 750

    def name(self):
        return 'sea'


class Alpine(Biome):
    def __init__(self):
        self.sustainable_population = 80

    def name(self):
        return 'alpine'


class Glacier(Biome):
    def __init__(self):
        self.sustainable_population = 0

    def name(self):
        return 'glacier'


class Iceland(Biome):
    def __init__(self):
        self.sustainable_population = 50

    def name(self):
        return 'iceland'


class Steppe(Biome):
    def __init__(self):
        self.sustainable_population = 100

    def name(self):
        return 'steppe'


class Grassland(Biome):
    def __init__(self):
        self.sustainable_population = 1000

    def name(self):
        return 'grassland'


class Jungle(Biome):
    def __init__(self):
        self.sustainable_population = 500

    def name(self):
        return 'jungle'


class Forest(Biome):
    def __init__(self):
        self.sustainable_population = 350

    def name(self):
        return 'forest'


class SandDesert(Biome):
    def __init__(self):
        self.sustainable_population = 50

    def name(self):
        return 'sand_desert'


class RockDesert(Biome):
    def __init__(self):
        self.sustainable_population = 75

    def name(self):
        return 'rock_desert'


class Savanna(Biome):
    def __init__(self):
        self.sustainable_population = 150

    def name(self):
        return 'savanna'


class Tundra(Biome):
    def __init__(self):
        self.sustainable_population = 60

    def name(self):
        return 'tundra'


class Swamp(Biome):
    def __init__(self):
        self.sustainable_population = 90

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
