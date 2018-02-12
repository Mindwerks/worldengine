import numpy

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


def temp_threshold(t):
    
    temps=[float("inf"),0.874, 0.765, 0.594, 0.439, 0.366, 0.124,-float("inf")]
    
    temp_keys=["polar","subpolar","boreal","cool","warm","subtropical","tropical"]
    
    temps.reverse()
    #temp_keys.reverse()
    
    r=l_threshold_map(t,temps,temp_keys)
    
    return r[0]

def humid_threshold(h):
    
    humids=[float("inf"),.941, .778, .507, .236, 0.073, .014, .002,-float("inf")]
    h_keys=["superarid","perarid","arid","semiarid","subhumid","humid","perhumid","superhumid"]
    
    humids.reverse()
    
    r=l_threshold_map(h,humids,h_keys)
    
    return r[0]

def threshold_map(value,thresholds):
    
    c=0
    m=len(thresholds)
    r_value=None
    while c < m-1:
        value_min = thresholds[c][1]
        value_max = thresholds[c+1][1]
        if value_min <= value <= value_max:
            r_value=thresholds[c+1][0]
            break
        c+=1
        
    if r_value==None:
        r_value=thresholds[-1][0]
        
    return r_value

def med(t1,t2):
    return (t1+t2)/2

def l_threshold_map(value,ts,names):
    c=0
    while c < len(ts)-1:
        if ts[c] <= value <=ts[c+1]:
            name=names[c]
            break
        c+=1
    return [ name , c , [ts[c],ts[c+1]] ]


class Biome:
    def __init__(self,name,temp_range,humid_range,color=None):
        self.name=name
        self.temp_range=temp_range
        self.humid_range=humid_range
        self.color=color

    def temp_check(self,t):
        return self.temp_range[0] <= t <=self.temp_range[1]
        
    def humid_check(self,h):
        return self.humid_range[0] <= t <=self.humid_range[1]
        
        
def assemble_biome_name(t_key,h_key):
    #"very dry",
    #humid_adj_list=["dry","moist","wet","rain"]
    
    #humid_adj={ "superarid":"",
                #"perarid":"",
                #"arid":"very dry",
                #"semiarid":"dry",
                #"subhumid":"",
                #"humid":"wet",
                #"perhumid":"rain",
                #"superhumid":"rain"}
    
    #humid_keys=list(humid_adj.keys())
    
    humid_veg={"superarid":"desert",
                "perarid":"scrub",
                "arid":"steppe",
                "semiarid":"dry woodland",
                "subhumid":"woodland",
                "humid":"forest",
                "perhumid":"wet forest",
                "superhumid":"rain forest"}
                
    #adj=humid_adj[h_key]
    vegetation=humid_veg[h_key]
    
    if t_key in ["warm","cool"]:
        t_key+=" temperate"
        
    if t_key == "subpolar":
        vegetation="tundra"
    
    if t_key=="polar" and h_key=="superarid":
        s=""
        s+=t_key+" "+humid_veg[h_key]
        return s
    elif t_key=="polar":
        return "ice"
    
    s=t_key+" "+vegetation
    s=s.split()
    sn=""
    for i in s:
        sn+=" "+i
    s=sn
    s=s.strip()
    
    return s
    
def biome_color(temp,humidity,hum_frac):
    
    if temp=="polar" and humidity!="superarid":
        color=(255, 255, 255) #ice 
        #maybe I can do something similar
        #for snow later.
        
        #'sea': (23, 94, 145),
        return color
    
    colors={
            "polar":(192, 192, 192),
            "subpolar":(128,128,128),#"tundra"
            "boreal":(160,160,128),
            "cool":(192,192,128),
            "warm":(224,224,128),
            "subtropical":(240,240,128),
            "tropical":(255,255,128)}
    #"ice":(255, 255, 255),
    
    color=colors[temp]
    color=(int((1-hum_frac)*color[0]),color[1],color[2])
    
    return color

def biome_matrix():
    
    temps=[float("inf"),0.874, 0.765, 0.594, 0.439, 0.366, 0.124,-float("inf")]
    temps.reverse()
    temp_keys=["polar","subpolar","boreal","cool","warm","subtropical","tropical"]
    #print(temp_keys)
    humids=[float("inf"),.941, .778, .507, .236, 0.073, .014, .002,-float("inf")]
    humids.reverse()
    h_keys=["superarid","perarid","arid","semiarid","subhumid","humid","perhumid","superhumid"]
    
    t=temps
    h=humids
    
    c=0
    a=[]
    while c < len(temps)-1:
        a.append([])
        c2=0
        while c2 < len(humids)-1:
            a[-1].append([med(t[c],t[c+1]),med(h[c2],h[c2+1])])
            c2+=1
        c+=1
    
    height,width=len(humids)-1,len(temps)-1
    
    mismatching=0
    total=0
    biome_cm={}
    
    all_bs={}
    biome=[]
    for y in range(height):
        biome.append([0]*width)
        for x in range(width):
            
            t = a[x][y][0]
            h = a[x][y][1]
            
            temp_zone,temp_index,temp_range=l_threshold_map(t,temps,temp_keys)
            
            humidity_zone,hum_index,hum_range=l_threshold_map(h,humids,h_keys)
            
            name=assemble_biome_name(temp_zone,humidity_zone)
            
            hum_frac=hum_index/len(humids)
            color=biome_color(temp_zone,humidity_zone,hum_frac)
            
            B=Biome(name,temp_range,hum_range,color)
            
            if name not in all_bs:
                all_bs.update({name:B})
                
            biome[y][x]=B
            
            if not biome[y][x] in biome_cm:
                biome_cm[biome[y][x]] = 0
            biome_cm[biome[y][x]] += 1
                
    biome=numpy.array(biome)
    return biome , all_bs   #biome_dict
    

def reformat_humidity_thresholds(h_thresholds):
    
    new_hs={}
    hum_strs=["superhumid","perhumid","humid","semihumid","semiarid","arid","perarid","superarid"]
    
    l=[]
    c=0
    for q in h_thresholds:
        
        new_key=int(q)
        l.append(new_key)
        
    l.sort()
    n_l=[]
    c=0
    for key in l:
        value=h_thresholds[str(key)]
        n_l.append((hum_strs[c],value))
        c+=1
    h_thresholds=n_l
    
    h_thresholds.insert(0,("none",h_thresholds[0][1]+0.1))
    h_thresholds.append(("superarid",h_thresholds[-1][1]-0.1))
    
    h_thresholds.reverse()
    return h_thresholds
    
def create_biome_map(ocean,temperature_map,humidity_map):#h_thresholds):
    
    simple_array,biome_dict=biome_matrix()
        
    shape=ocean.shape
    height,width=shape
    
    biome_cm = {}
    biome = numpy.zeros((height, width), dtype = object)#this is still kind of expensive memory-wise
    ocean_B=Biome("ocean",None,None,(23, 94, 145))
    for y in range(height):
        for x in range(width):
            
            t = temperature_map[y,x]
            h = humidity_map[y,x]
            
            if ocean[y, x]:
                biome[y, x] = ocean_B
                
            else:
                temp_zone = temp_threshold(t)#l_threshold_map(t,temps,temp_keys)#t_thresholds)
                humidity_zone = humid_threshold(h)# l_threshold_map(h,humids,h_keys)#h_thresholds)
                
                name=assemble_biome_name(temp_zone,humidity_zone)
                
                B=biome_dict[name]
                biome[y,x]=B
                
            if not biome[y, x] in biome_cm:
                biome_cm[biome[y, x]] = 0
            biome_cm[biome[y, x]] += 1
    
    #print(new_m[0][0])
    return biome_cm, biome

def blow_up_matrix(m,factor=10):
    h=len(m)
    w=len(m[0])
    c=0
    new_m=[]
    while c < h:
        new_m.append([])
        c2=0
        while c2 < w:
            bc=0
            while bc < factor:
                #blow up the row
                new_m[-1].append(m[c][c2])
                bc+=1
            c2+=1
        
        #multiply the rows
        bc=1
        while bc < factor:
            new_m.append(new_m[-1])
            bc+=1
        c+=1
    new_m=numpy.array(new_m)
    return new_m


    #return cm, biome_cm,biome
if __name__=="__main__":
    #assign_biomes(None,None)
    from worldengine.draw import draw_biome_on_file
    
    #biome_matrix()
    m,biome_dict=biome_matrix()
    m=blow_up_matrix(m)
    draw_biome_on_file(m,"testbiome.png")
