class Race(object):
    pass
    
class Human(Race):

    def name(self):
        return 'human'

    def sustainable_population(self,biome):
        return biome.sustainable_population

    def aggressiveness(self):
        return 0.5

    def war_power(self):
        return 0.5

    def governability(self):
        return 0.8

    def expansion_eagerness(self):
        return 0.9

class Orc(Race):

    # tribal
    # high strength
    # high aggressivness

    def name(self):
        return 'orc'

    def sustainable_population(self,biome):
        value = {
            'ocean':0.0,
            'sea':0.0,
            'savanna':1.8,
            'alpine':1.0,
            'glacier':1.2,
            'iceland':1.2,
            'jungle':1.2,
            'rock_desert':2.5,
            'sand_desert':0.5,
            'grassland':0.5,
            'forest':1.3,
            'tundra':1.5        
        }
        return int(value[biome.name()]*biome.sustainable_population)

    def aggressiveness(self):
        return 1.0

    def war_power(self):
        return 0.8

    def governability(self):
        return 0.2

    def expansion_eagerness(self):
        return 1.0        

class Elf(Race):

    def name(self):
        return 'elves'    
    
    def sustainable_population(self,biome):
        value = {
            'ocean':0.0,
            'sea':0.0,
            'savanna':0.2,
            'alpine':0.2,
            'glacier':1.2,
            'iceland':1.2,
            'jungle':1.2,
            'rock_desert':0.2,
            'sand_desert':0.2,
            'grassland':0.3,
            'forest':3.0,
            'tundra':2.3        
        }
        return int(value[biome.name()]*biome.sustainable_population)

    def aggressiveness(self):
        return 0.2

    def war_power(self):
        return 0.7

    def governability(self):
        return 0.9

    def expansion_eagerness(self):
        return 0.2        
                    
class Dwarf(Race):

    def name(self):
        return 'dwarf'

    def sustainable_population(self,biome):
        value = {
            'ocean':0.0,
            'sea'  :0.0,
            'savanna':0.1,
            'alpine' :10.0,
            'glacier':5.0,
            'iceland':2.0,
            'jungle':0.1,
            'rock_desert':0.1,
            'sand_desert':0.1,
            'grassland':0.45,
            'forest':0.3,
            'tundra':0.7        
        }
        mul = value[biome.name()]
        base = biome.sustainable_population
        return int(mul*base)

    def aggressiveness(self):
        return 0.7

    def war_power(self):
        return 0.88

    def governability(self):
        return 0.5

    def expansion_eagerness(self):
        return 0.6