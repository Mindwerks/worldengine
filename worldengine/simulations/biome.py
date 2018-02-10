import numpy




biome_colors = {
    'ocean': (23, 94, 145),
    'sea': (23, 94, 145),
    'ice': (255, 255, 255),
    'subpolar dry tundra': (128, 128, 128),
    'subpolar moist tundra': (96, 128, 128),
    'subpolar wet tundra': (64, 128, 128),
    'subpolar rain tundra': (32, 128, 192),
    'polar desert': (192, 192, 192),
    'boreal desert': (160, 160, 128),
    'cool temperate desert': (192, 192, 128),
    'warm temperate desert': (224, 224, 128),
    'subtropical desert': (240, 240, 128),
    'tropical desert': (255, 255, 128),
    'boreal rain forest': (32, 160, 192),
    'cool temperate rain forest': (32, 192, 192),
    'warm temperate rain forest': (32, 224, 192),
    'subtropical rain forest': (32, 240, 176),
    'tropical rain forest': (32, 255, 160),
    'boreal wet forest': (64, 160, 144),
    'cool temperate wet forest': (64, 192, 144),
    'warm temperate wet forest': (64, 224, 144),
    'subtropical wet forest': (64, 240, 144),
    'tropical wet forest': (64, 255, 144),
    'boreal moist forest': (96, 160, 128),
    'cool temperate moist forest': (96, 192, 128),
    'warm temperate moist forest': (96, 224, 128),
    'subtropical moist forest': (96, 240, 128),
    'tropical moist forest': (96, 255, 128),
    'warm temperate dry forest': (128, 224, 128),
    'subtropical dry forest': (128, 240, 128),
    'tropical dry forest': (128, 255, 128),
    'boreal dry scrub': (128, 160, 128),
    'cool temperate desert scrub': (160, 192, 128),
    'warm temperate desert scrub': (192, 224, 128),
    'subtropical desert scrub': (208, 240, 128),
    'tropical desert scrub': (224, 255, 128),
    'cool temperate steppe': (128, 192, 128),
    'warm temperate thorn scrub': (160, 224, 128),
    'subtropical thorn woodland': (176, 240, 128),
    'tropical thorn woodland': (192, 255, 128),
    'tropical very dry forest': (160, 255, 128),
}

# These colors are used when drawing the satellite view map
# The rgb values were hand-picked from an actual high-resolution 
# satellite map of earth. However, many values are either too similar
# to each other or otherwise need to be updated. It is recommended that
# further research go into these values, making sure that each rgb is
# actually picked from a region on earth that has the matching biome
_biome_satellite_colors = {
    'ocean': (23, 94, 145),
    'sea': (23, 94, 145),
    'ice': (255, 255, 255),
    'subpolar dry tundra': (186, 199, 206),
    'subpolar moist tundra': (186, 195, 202),
    'subpolar wet tundra': (186, 195, 204),
    'subpolar rain tundra': (186, 200, 210),
    'polar desert': (182, 195, 201),
    'boreal desert': (132, 146, 143),
    'cool temperate desert': (183, 163, 126),
    'warm temperate desert': (166, 142, 104),
    'subtropical desert': (205, 181, 137),
    'tropical desert': (203, 187, 153),
    'boreal rain forest': (21, 29, 8),
    'cool temperate rain forest': (25, 34, 15),
    'warm temperate rain forest': (19, 28, 7),
    'subtropical rain forest': (48, 60, 24),
    'tropical rain forest': (21, 38, 6),
    'boreal wet forest': (6, 17, 11),
    'cool temperate wet forest': (6, 17, 11),
    'warm temperate wet forest': (44, 48, 19),
    'subtropical wet forest': (23, 36, 10),
    'tropical wet forest': (23, 36, 10),
    'boreal moist forest': (31, 39, 18),
    'cool temperate moist forest': (31, 39, 18),
    'warm temperate moist forest': (36, 42, 19),
    'subtropical moist forest': (23, 31, 10),
    'tropical moist forest': (24, 36, 11),
    'warm temperate dry forest': (52, 51, 30),
    'subtropical dry forest': (53, 56, 30),
    'tropical dry forest': (54, 60, 30),
    'boreal dry scrub': (73, 70, 61),
    'cool temperate desert scrub': (80, 58, 44),
    'warm temperate desert scrub': (92, 81, 49),
    'subtropical desert scrub': (68, 57, 35),
    'tropical desert scrub': (107, 87, 60),
    'cool temperate steppe': (95, 82, 50),
    'warm temperate thorn scrub': (77, 81, 48),
    'subtropical thorn woodland': (27, 40, 12),
    'tropical thorn woodland': (40, 62, 15),
    'tropical very dry forest': (87, 81, 49),
}



class BiomeSimulation(object):

    @staticmethod
    def is_applicable(world):
        return world.has_humidity() and world.has_temperature() and not world.has_biome()

    @staticmethod
    def execute(world, seed):
        assert seed is not None
        w = world
        width = world.width
        height = world.height
        ocean = world.layers['ocean'].data
        cm = {}
        biome_cm = {}
        biome = numpy.zeros((height, width), dtype = object)#this is still kind of expensive memory-wise
        for y in range(height):
            for x in range(width):
                if ocean[y, x]:
                    biome[y, x] = 'ocean'
                else:
                    if w.is_temperature_polar((x, y)):
                        if w.is_humidity_superarid((x, y)):
                            biome[y, x] = 'polar desert'
                        else:
                            biome[y, x] = 'ice'
                    elif w.is_temperature_alpine((x, y)):
                        if w.is_humidity_superarid((x, y)):
                            biome[y, x] = 'subpolar dry tundra'
                        elif w.is_humidity_perarid((x, y)):
                            biome[y, x] = 'subpolar moist tundra'
                        elif w.is_humidity_arid((x, y)):
                            biome[y, x] = 'subpolar wet tundra'
                        else:
                            biome[y, x] = 'subpolar rain tundra'
                    elif w.is_temperature_boreal((x, y)):
                        if w.is_humidity_superarid((x, y)):
                            biome[y, x] = 'boreal desert'
                        elif w.is_humidity_perarid((x, y)):
                            biome[y, x] = 'boreal dry scrub'
                        elif w.is_humidity_arid((x, y)):
                            biome[y, x] = 'boreal moist forest'
                        elif w.is_humidity_semiarid((x, y)):
                            biome[y, x] = 'boreal wet forest'
                        else:
                            biome[y, x] = 'boreal rain forest'
                    elif w.is_temperature_cool((x, y)):
                        if w.is_humidity_superarid((x, y)):
                            biome[y, x] = 'cool temperate desert'
                        elif w.is_humidity_perarid((x, y)):
                            biome[y, x] = 'cool temperate desert scrub'
                        elif w.is_humidity_arid((x, y)):
                            biome[y, x] = 'cool temperate steppe'
                        elif w.is_humidity_semiarid((x, y)):
                            biome[y, x] = 'cool temperate moist forest'
                        elif w.is_humidity_subhumid((x, y)):
                            biome[y, x] = 'cool temperate wet forest'
                        else:
                            biome[y, x] = 'cool temperate rain forest'
                    elif w.is_temperature_warm((x, y)):
                        if w.is_humidity_superarid((x, y)):
                            biome[y, x] = 'warm temperate desert'
                        elif w.is_humidity_perarid((x, y)):
                            biome[y, x] = 'warm temperate desert scrub'
                        elif w.is_humidity_arid((x, y)):
                            biome[y, x] = 'warm temperate thorn scrub'
                        elif w.is_humidity_semiarid((x, y)):
                            biome[y, x] = 'warm temperate dry forest'
                        elif w.is_humidity_subhumid((x, y)):
                            biome[y, x] = 'warm temperate moist forest'
                        elif w.is_humidity_humid((x, y)):
                            biome[y, x] = 'warm temperate wet forest'
                        else:
                            biome[y, x] = 'warm temperate rain forest'
                    elif w.is_temperature_subtropical((x, y)):
                        if w.is_humidity_superarid((x, y)):
                            biome[y, x] = 'subtropical desert'
                        elif w.is_humidity_perarid((x, y)):
                            biome[y, x] = 'subtropical desert scrub'
                        elif w.is_humidity_arid((x, y)):
                            biome[y, x] = 'subtropical thorn woodland'
                        elif w.is_humidity_semiarid((x, y)):
                            biome[y, x] = 'subtropical dry forest'
                        elif w.is_humidity_subhumid((x, y)):
                            biome[y, x] = 'subtropical moist forest'
                        elif w.is_humidity_humid((x, y)):
                            biome[y, x] = 'subtropical wet forest'
                        else:
                            biome[y, x] = 'subtropical rain forest'
                    elif w.is_temperature_tropical((x, y)):
                        if w.is_humidity_superarid((x, y)):
                            biome[y, x] = 'tropical desert'
                        elif w.is_humidity_perarid((x, y)):
                            biome[y, x] = 'tropical desert scrub'
                        elif w.is_humidity_arid((x, y)):
                            biome[y, x] = 'tropical thorn woodland'
                        elif w.is_humidity_semiarid((x, y)):
                            biome[y, x] = 'tropical very dry forest'
                        elif w.is_humidity_subhumid((x, y)):
                            biome[y, x] = 'tropical dry forest'
                        elif w.is_humidity_humid((x, y)):
                            biome[y, x] = 'tropical moist forest'
                        elif w.is_humidity_perhumid((x, y)):
                            biome[y, x] = 'tropical wet forest'
                        else:
                            biome[y, x] = 'tropical rain forest'
                    else:
                        biome[y, x] = 'bare rock'
                if not biome[y, x] in biome_cm:
                    biome_cm[biome[y, x]] = 0
                biome_cm[biome[y, x]] += 1
                
        w.biome = biome
        return cm, biome_cm


def map_value(x,y,val_map,values,val_keys):

    val= val_map[x,y]
    
    c=0
    m=len(values)
    while c < m-1:
        val_i =values[c]
        val_ii=values[c+1]
        if val_i <= val <= val_ii:
            val_key=value_keys[val_i]
            break
            
    return val_key

def humidity_keys():
    
    aridity=["arid","humid"]
    quantifiers=["super","per"," ","semi","sub"]
    
    ard_q=[]
    #for gq in aridity:
    r=[]
    gq="arid"
    for q in quantifiers:
        r.append((q+" "+gq).strip())
    r2=[]
    gq="humid"
    for q in quantifiers:
        r2.append((q+" "+gq).strip())
    r2.reverse()
    ard_q=r[:-1]+r2
    return ard_q


class Biome:
    def __init__(self,temp_range,humidity_range,color):
        self.temperature_range=temp_range
        self.humidity_range=humidity_range
        self.color=color
        
    def name(self):
        n=""
        return n
    

def pick_biome(x,y,biomes):
    a=1
    
def assign_biomes(temp_map,humid_map):
    #height,width=ocean.shape
    
    biomes=[]
    
    temps=[0.874, 0.765, 0.594, 0.439, 0.366, 0.124,0]
    temperatures_keys=["polar","subpolar","boreal","cool","warm","subtropical","tropical"]
    
    shape=(10,10)
    
    for y in [1,2]:#range([0,shape[0]):
        for x in [1,2]:#range([0,shape[1]]):
            s=""
            
            b=pick_biome(x,y,biomes)
            #map [x,y] = b
            #print(x,y)
            continue
            t_key=map_value(x,y,temps_map,temps,temperatures_keys)
            s+=t_key
            
            h_key=map_value(x,y,humid_map,humids,humid_keys)
            s+=h_key
        
    
    x,y=0,0
    
    veg_adj=["thorn","rain"]
    
    t_to_veg={"alpine":["tundra"],
            "boreal":["desert","scrub","forest"],
            "cool":["desert","scrub","forets"],
            "warm":["desert","scrub","forets"],
            "subtropical":["desert","scrub","forets"],
            "tropical":["desert","scrub","woodland","forest"]
            }
            
    humids=[.941, .778, .507, .236, 0.073, .014, .002]
    vegetation_keys=["desert","steppe","scrub","woodland","forest"]
    humidities_keys=["dry","moist","rain"]
    
    
    
    #return cm, biome_cm,biome
if __name__=="__main__":
    assign_biomes(None,None)
