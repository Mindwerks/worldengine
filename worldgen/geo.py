import random
import math
from noise import snoise2
import jsonpickle

WIDTH    = 512
HEIGHT   = 512
N_PLATES = 32
MIN_ELEV = 0
MAX_ELEV = 255
MAX_DIST = 6

def random_point():
    return (random.randrange(0,WIDTH),random.randrange(0,HEIGHT))

def distance(pa,pb):
    ax,ay = pa
    bx,by = pb
    return math.sqrt((ax-bx)**2+(ay-by)**2)

def nearest(p,hot_points):
    min_dist     = None
    nearest_hp_i = None
    for i, hp in enumerate(hot_points):
        dist = distance(p,hp)
        if (None==min_dist) or dist<min_dist:
            min_dist = dist
            nearest_hp_i = i
    return nearest_hp_i

def generate_plates(seed):
    N_HOT_POINTS = 512

    random.seed(seed)

    # generate hot points
    hot_points = [random_point() for i in range(N_HOT_POINTS)]

    # generate plate-origins
    plate_origins = [random_point() for i in range(N_PLATES)]

    # assign hot points to plate plate-origins
    hot_points_to_plates = [nearest(hp,plate_origins) for hp in hot_points]

    # assign each tile to hot points
    tiles_to_plates = []
    for y in range(0,HEIGHT):
        row = []
        for x in range(0,WIDTH):
            hp_i = nearest((x,y),hot_points)
            hp = hot_points[hp_i]
            plate_i = nearest(hp,plate_origins)
            row.append(plate_i)
        tiles_to_plates.append(row)
    return tiles_to_plates

def plate_borders(plates):  

    def calc_borders(x,y,p):
        borders = []
        for dy in range(-MAX_DIST,+MAX_DIST+1):
            py = y+dy
            if py>0 and py<HEIGHT:
                for dx in range(-MAX_DIST,+MAX_DIST+1):
                    px = x+dx
                    if px>0 and px<WIDTH:
                        pp = plates[py][px]
                        if pp!=p:
                            borders.append((p,pp))
        return borders  

    borders = []
    for y in range(0,HEIGHT):
        row = []
        for x in range(0,WIDTH):
            p = plates[y][x]
            row.append(calc_borders(x,y,p))
        borders.append(row)
    return borders

def watermap(world,n,_watermap=None):

    def droplet(world,pos,q,_watermap):
        if q<0:
            return
        x,y = pos
        pos_elev = world.elevation['data'][y][x]+_watermap[y][x]
        lowers  = []
        min_higher = None
        min_lower  = None
        pos_min_higher = None
        tot_lowers = 0
        for p in world.tiles_around((x,y)):
            px,py = p
            e = world.elevation['data'][py][px]+_watermap[py][px]
            if e<pos_elev:
                dq = int(pos_elev-e)<<2
                if min_lower==None or e<min_lower:
                    min_lower=e
                    if dq==0:
                        dq=1
                lowers.append((dq,p))
                tot_lowers += dq
                
            else:
                if min_higher==None or e>min_higher:
                    min_higher=e
                    pos_min_higher = p
        if lowers:
            f = q/tot_lowers
            for l in lowers:
                s,p = l
                if world.is_land(p):
                    px,py = p
                    ql = f*s
                    #ql = q
                    going = ql>0.05
                    _watermap[py][px] += ql
                    if going:
                        droplet(world,p,ql,_watermap) 
        else:
            _watermap[y][x] += q

    if _watermap==None:
        _watermap = [[0 for x in xrange(world.width)] for y in xrange(world.height)] 
    for i in xrange(n):
        x,y = world.random_land()
        if True and world.precipitation['data'][y][x]>0:
            droplet(world,(x,y),world.precipitation['data'][y][x],_watermap)    
    return _watermap


def erode(world,n):

    def droplet(world,pos,q,v):
        if q<0:
            raise Exception('why?')
        x,y = pos
        pos_elev = world.elevation['data'][y][x]
        lowers  = []
        min_higher = None
        min_lower  = None
        tot_lowers = 0
        for p in world.tiles_around((x,y)):
            px,py = p
            e = world.elevation['data'][py][px]
            if e<pos_elev:
                dq = int(pos_elev-e)<<2
                if dq==0:
                    dq=1
                lowers.append((dq,p))
                tot_lowers += dq
                if min_lower==None or e<min_lower:
                    min_lower=e
            else:
                if min_higher==None or e>min_higher:
                    min_higher=e
        if lowers:
            f = q/tot_lowers
            for l in lowers:
                s,p = l
                if world.is_land(p):
                    px,py = p
                    ql = f*s
                    if ql<0:
                        raise Exception('Why ql<0? f=%f s=%f' % (f,s))
                    #if ql<0.8*q:
                    #    ql = q # rafforzativo
                    #ql = q
                    #going = world.elevation['data'][py][px]==min_higher
                    going = ql>0.05
                    world.elevation['data'][py][px] -= ql
                    if going:
                        droplet(world,p,ql,0) 
                    #elif random.random()<s:
                    #    droplet(world,p,ql,0) 
        else:
            world.elevation['data'][y][x]+=0.3
            if world.elevation['data'][y][x]>min_higher:
                world.elevation['data'][y][x] = min_higher
            #world.elevation['data'][y][x] = min_higher

    for i in xrange(n):
        x,y = world.random_land()
        if True and world.precipitation['data'][y][x]>0:
            droplet(world,(x,y),world.precipitation['data'][y][x]*1,0)  

def matrix_extremes(matrix):
    min = None
    max = None
    for row in matrix:
        for el in row:
            val = el
            if min==None or val<min:
                min=val
            if max==None or val>max:
                max=val
    return (min,max)

def rescale_value(original,prev_min,prev_max,min,max):
    f = float(original-prev_min)/(prev_max-prev_min)
    return min+((max-min)*f)

def sea_depth(world,sea_level):
    sea_depth = [[sea_level-world.elevation['data'][y][x] for x in xrange(world.width)] for y in xrange(world.height)]
    for y in xrange(world.height):
        for x in xrange(world.width):
            if world.tiles_around((x,y),radius=1,predicate=world.is_land):
                sea_depth[y][x] = 0
            elif world.tiles_around((x,y),radius=2,predicate=world.is_land):
                sea_depth[y][x] *= 0.3
            elif world.tiles_around((x,y),radius=3,predicate=world.is_land):
                sea_depth[y][x] *= 0.5
            elif world.tiles_around((x,y),radius=4,predicate=world.is_land):
                sea_depth[y][x] *= 0.7
            elif world.tiles_around((x,y),radius=5,predicate=world.is_land):
                sea_depth[y][x] *= 0.9                            
    antialias(sea_depth,10)  
    min_depth,max_depth = matrix_extremes(sea_depth)
    sea_depth = [[rescale_value(sea_depth[y][x],min_depth,max_depth,0.0,1.0) for x in xrange(world.width)] for y in xrange(world.height)]
    return sea_depth

def antialias(elevation,steps):

    def antialias():
        for y in range(0,HEIGHT):
            for x in range(0,WIDTH):
                antialias_point(x,y)        

    def antialias_point(x,y):   
        n = 2
        tot = elevation[y][x]*2
        for dy in range(-1,+2):
            py = y+dy
            if py>0 and py<HEIGHT:
                for dx in range(-1,+2):
                    px = x+dx
                    if px>0 and px<WIDTH:
                        n += 1
                        tot += elevation[py][px]
        return tot/n

    for i in range(0,steps):
        antialias()

def elevnoise(elevation,seed):  
    octaves = 6
    freq = 16.0 * octaves
    for y in range(0,HEIGHT):
        for x in range(0,WIDTH):
            n = int(snoise2(x / freq*2, y / freq*2, octaves, base=seed) * 127.0 + 128.0)
            elevation[y][x]+=n/2

def generate_base_heightmap(seed,plates):

    OCEAN_BORDER = 20

    def at_border(i):
        for y in range(0,HEIGHT):
            if plates[y][0]==i or plates[y][WIDTH-1]==i:
                return True
        for x in range(0,WIDTH):
            if plates[0][x]==i or plates[HEIGHT-1][x]==i:
                return True
        return False

    def random_plate_elev(i):
        if at_border(i):
            base = 0
        else:
            base = random.choice([20,25,80,90,100])
        return base+random.randrange(0,25)

    def consider_borders(elevation):
        from noise import pnoise2, snoise2
        base = random.randint(0,4096)
        octaves = 3
        freq = 16.0 * octaves

        pbs = plate_borders(plates)
        deltas = {}
        for y in range(0,HEIGHT):
            for x in range(0,WIDTH):
                deltatot = 0
                for b in pbs[y][x]:
                    if not (b in deltas):
                        deltas[b] = random.randrange(-2,2)*random.randrange(0,2)*random.randrange(0,2)
                    deltatot += deltas[b]

                elevation[y][x] += (deltatot/10)*((snoise2(x / freq*2, y / freq*2, octaves, base=base)+1.0))

    def place_ocean(x,y,i):
        elevation[y][x] = (elevation[y][x]*i)/OCEAN_BORDER

    def place_oceans_around(elevation):
        for y in range(0,HEIGHT):
            for i in range(0,OCEAN_BORDER):
                place_ocean(i,y,i)
                place_ocean(WIDTH-i-1,y,i)
        for x in range(0,WIDTH):
            for i in range(0,OCEAN_BORDER):
                place_ocean(x,i,i)
                place_ocean(x,HEIGHT-i-1,i)             
            
    random.seed(seed)

    # base elevation for each plate
    plate_elev = [random_plate_elev(i) for i in range(0,N_PLATES)]
    elevation = []
    for y in range(0,HEIGHT):
        row = []
        for x in range(0,WIDTH):
            elev = plate_elev[plates[y][x]]
            row.append(elev)
        elevation.append(row)

    # consider borders
    consider_borders(elevation)
    place_oceans_around(elevation)  
    antialias(elevation,5)
    elevnoise(elevation,random.randint(0,4096))

    return elevation

def find_threshold(elevation,land_perc,ocean=None):
    
    def count(e):
        tot = 0
        for y in range(0,HEIGHT):
            for x in range(0,WIDTH):
                if elevation[y][x]>e and (ocean==None or not ocean[y][x]):
                    tot+=1
        return tot

    def search(a,b,desired):
        if a==b:
            return a
        if (b-a)==1:
            ca = count(a)
            cb = count(b)
            dista = abs(desired-ca)
            distb = abs(desired-cb)
            if dista<distb:
                return a
            else:
                return b
        m = (a+b)/2
        cm = count(m)
        if desired<cm:
            return search(m,b,desired)
        else:
            return search(a,m,desired)

    all_land = WIDTH*HEIGHT
    if ocean:
        for y in range(0,HEIGHT):
            for x in range(0,WIDTH):
                if ocean[y][x]:
                    all_land-=1
    desired_land = all_land*land_perc
    return search(0,255,desired_land)

def find_threshold_f(elevation,land_perc,ocean=None):
    
    def count(e):
        tot = 0
        for y in range(0,HEIGHT):
            for x in range(0,WIDTH):
                if elevation[y][x]>e and (ocean==None or not ocean[y][x]):
                    tot+=1
        return tot

    def search(a,b,desired):
        if a==b:
            return a
        if abs(b-a)<0.005:
            ca = count(a)
            cb = count(b)
            dista = abs(desired-ca)
            distb = abs(desired-cb)
            if dista<distb:
                return a
            else:
                return b
        m = (a+b)/2.0
        cm = count(m)
        if desired<cm:
            return search(m,b,desired)
        else:
            return search(a,m,desired)

    all_land = WIDTH*HEIGHT
    if ocean:
        for y in range(0,HEIGHT):
            for x in range(0,WIDTH):
                if ocean[y][x]:
                    all_land-=1
    desired_land = all_land*land_perc
    return search(-1.0,2.0,desired_land)

def around(x,y):
    ps = []
    for dx in range(-1,2):
        nx = x+dx
        if nx>=0 and nx<WIDTH:
            for dy in range(-1,2):
                ny = y+dy
                if ny>=0 and ny<HEIGHT and (dx!=0 or dy!=0):
                    ps.append((nx,ny))
    return ps

def fill_ocean(elevation,sea_level):
    ocean = [[False for x in xrange(WIDTH)] for y in xrange(HEIGHT)] 
    to_expand = []
    for x in range(0,WIDTH):
        to_expand.append((x,0))
        to_expand.append((x,HEIGHT-1))
    for y in range(0,HEIGHT):
        to_expand.append((0,y))
        to_expand.append((WIDTH-1,y))
    for t in to_expand:
        tx,ty = t
        if not ocean[ty][tx]:
            ocean[ty][tx] = True
            for px,py in around(tx,ty):
                if not ocean[py][px] and elevation[py][px]<=sea_level:
                    to_expand.append((px,py))

    return ocean

def temperature(seed,elevation,mountain_level):
    random.seed(seed*7)
    base = random.randint(0,4096)
    temp = [[0 for x in xrange(WIDTH)] for y in xrange(HEIGHT)] 
    
    from noise import pnoise2, snoise2
    octaves = 6
    freq = 16.0 * octaves

    for y in range(0,HEIGHT):
        yscaled = float(y)/HEIGHT
        latitude_factor = 1.0-(abs(yscaled-0.5)*2)
        for x in range(0,WIDTH):
            n = snoise2(x / freq, y / freq, octaves,base=base)
            t = (latitude_factor*3+n*2)/5.0
            if elevation[y][x]>mountain_level:
                if elevation[y][x]>(mountain_level+29):
                    altitude_factor=0.033
                else:
                    altitude_factor = 1.00-(float(elevation[y][x]-mountain_level)/30)
                t*=altitude_factor
            temp[y][x] = t

    return temp

def precipitation(seed):
    random.seed(seed*13)
    base = random.randint(0,4096)
    temp = [[0 for x in xrange(WIDTH)] for y in xrange(HEIGHT)] 
    
    from noise import pnoise2, snoise2
    octaves = 6
    freq = 64.0 * octaves

    for y in range(0,HEIGHT):
        yscaled = float(y)/HEIGHT
        latitude_factor = 1.0-(abs(yscaled-0.5)*2)
        for x in range(0,WIDTH):
            n = snoise2(x / freq, y / freq, octaves, base=base)
            t = (latitude_factor+n*4)/5.0
            temp[y][x] = t

    return temp

def irrigation(world):
    values = [[0 for x in xrange(WIDTH)] for y in xrange(HEIGHT)] 
    radius = 10
    
    for y in xrange(HEIGHT):
        for x in xrange(WIDTH):
            if world.is_land((x,y)):
                for dy in range(-radius,radius+1):
                    if (y+dy)>=0 and (y+dy)<world.height:
                        for dx in range(-radius,radius+1):
                            if (x+dx)>=0 and (x+dx)<world.width:
                                dist = math.sqrt(dx**2+dy**2)
                                values[y+dy][x+dx] += world.watermap[y][x]/(math.log(dist+1)+1)

    return values

def permeability(seed):
    random.seed(seed*37)
    base = random.randint(0,4096)
    temp = [[0 for x in xrange(WIDTH)] for y in xrange(HEIGHT)] 
    
    from noise import pnoise2, snoise2
    octaves = 6
    freq = 64.0 * octaves

    for y in range(0,HEIGHT):
        yscaled = float(y)/HEIGHT
        for x in range(0,WIDTH):
            n = snoise2(x / freq, y / freq, octaves, base=base)
            t = n
            temp[y][x] = t

    return temp     

def classify(data,thresholds,x,y):
    value = data[y][x]
    for name,level in thresholds:
        if (level==None) or (value<level):
            return name

import operator

class World(object):

    def __init__(self,name):
        self.name = name
        self.width = 512
        self.height = 512

    def is_mountain(self,pos):
        if not self.is_land(pos):
            return False
        if len(self.elevation['thresholds'])==4:
            mi = 2
        else:
            mi = 1
        mountain_level = self.elevation['thresholds'][mi][1]
        x,y = pos
        return self.elevation['data'][y][x]>mountain_level

    def is_hill(self,pos):
        if not self.is_land(pos):
            return False
        if len(self.elevation['thresholds'])==4:
            hi = 1
        else:
            hi = 0
        hill_level = self.elevation['thresholds'][hi][1]
        mountain_level = self.elevation['thresholds'][hi+1][1]
        x,y = pos
        return self.elevation['data'][y][x]>hill_level and self.elevation['data'][y][x]<mountain_level

    def is_temperature_very_low(self,pos):
        th_max = self.temperature['thresholds'][0][1]
        x,y = pos
        t = self.temperature['data'][y][x]
        return t<th_max

    def is_temperature_low(self,pos):
        th_min = self.temperature['thresholds'][0][1]
        th_max = self.temperature['thresholds'][1][1]
        x,y = pos
        t = self.temperature['data'][y][x]
        return t<th_max and t>=th_min

    def is_temperature_medium(self,pos):
        th_min = self.temperature['thresholds'][1][1]
        th_max = self.temperature['thresholds'][2][1]
        x,y = pos
        t = self.temperature['data'][y][x]
        return t<th_max and t>=th_min

    def is_temperature_high(self,pos):
        th_min = self.temperature['thresholds'][2][1]
        x,y = pos
        t = self.temperature['data'][y][x]
        return t>=th_min


    def set_biome(self,biome):
        self.biome = biome

    def set_ocean(self,ocean):
        self.ocean = ocean

    def set_elevation(self,data,thresholds):
        self.elevation = {'data':data,'thresholds':thresholds}

    def set_precipitation(self,data,thresholds):
        self.precipitation = {'data':data,'thresholds':thresholds}

    def set_temperature(self,data,thresholds):
        self.temperature = {'data':data,'thresholds':thresholds}

    def set_permeability(self,data,thresholds):
        self.permeability = {'data':data,'thresholds':thresholds}

    def random_land(self):
        x,y = random_point()
        if self.ocean[y][x]:
            return self.random_land()
        else:
            return (x,y)

    def is_land(self,pos):
        x,y = pos
        return not self.ocean[y][x]

    def tiles_around(self,pos,radius=1,predicate=None):
        ps = []
        x,y = pos
        for dx in range(-radius,radius+1):
            nx = x+dx
            if nx>=0 and nx<self.width:
                for dy in range(-radius,radius+1):
                    ny = y+dy
                    if ny>=0 and ny<self.height and (dx!=0 or dy!=0):
                        if predicate==None or predicate((nx,ny)):
                            ps.append((nx,ny))
        return ps       

    def tiles_around_many(self,pos_list,radius=1,predicate=None):
        tiles = []
        for pos in pos_list:
            tiles += self.tiles_around(pos,radius,predicate)
        # remove duplicates
        # remove elements in pos
        return list(set(tiles)-set(pos_list))

    def biome_at(self,pos):
        x,y = pos
        b = Biome.by_name(self.biome[y][x])
        if b==None:
            raise Exception('Not found')
        return b

    def sustainable_population(self,pos):
        return self.biome_at(pos).sustainable_population

    @classmethod
    def from_json_file(self,filename):
        with open(filename, "r") as f:
            content = f.read()
        world = jsonpickle.decode(content)
        world.width = world.height = 512
        if type(world) is World:
            return world
        else:
            return self.from_dict(world)

    @classmethod
    def from_dict(self,dict):

        def map_from_dict(md):
            m = []
            for row_dict in md:
                row = []
                for col_dict in row_dict:
                    row.append(col_dict)
                m.append(row)
            return m

        def thresholds_from_dict(td):
            t = []
            return t

        def mapwt_from_dict(md):
            return (map_from_dict(md['data'],thresholds_from_dict(md['thresholds'])))

        instance = World(dict['name'])
        instance.set_biome(map_from_dict(dict['biome']))
        instance.set_ocean(map_from_dict(dict['ocean']))
        instance.set_precipitation(map_from_dict(dict['precipitation']['data']),[])
        instance.set_temperature(map_from_dict(dict['temperature']['data']),[])
        return instance


def world_gen(name,seed,verbose=False):
    plates = generate_plates(seed)
    e = generate_base_heightmap(seed,plates)
    w = world_gen_from_elevation(name,e,seed,verbose=verbose)
    return w

def humidity(world):
    humidity = {}
    humidity['data'] = [[0 for x in xrange(world.width)] for y in xrange(world.height)] 
    
    for y in xrange(world.height):
        for x in xrange(world.width):
            humidity['data'][y][x] = world.precipitation['data'][y][x]+world.irrigation[y][x]

    humidity['quantiles'] = {}
    humidity['quantiles'][33] = find_threshold_f(humidity['data'],0.33,world.ocean)
    humidity['quantiles'][50] = find_threshold_f(humidity['data'],0.50,world.ocean) 
    humidity['quantiles'][66] = find_threshold_f(humidity['data'],0.66,world.ocean) 
    return humidity

def world_gen_from_elevation(name,elevation,seed,verbose=False):
    i = seed
    w = World(name)

    # Elevation with thresholds
    e = elevation
    sl = find_threshold(e,0.3)
    ocean = fill_ocean(e,sl+1.5)
    hl = find_threshold(e,0.10)
    ml = find_threshold(e,0.03)
    e_th = [('sea',sl),('plain',hl),('hill',ml),('mountain',None)]
    w.set_ocean(ocean)
    w.set_elevation(e,e_th)
    w.sea_depth = sea_depth(w,sl)
    if verbose:
        print("...elevation level calculated")

    # Precipitation with thresholds
    p = precipitation(i)
    p_th = [
        ('low',find_threshold_f(p,0.75,ocean)),
        ('med',find_threshold_f(p,0.3,ocean)),
        ('hig',None)
    ]
    w.set_precipitation(p,p_th)

    erode(w,3000000)
    if verbose:
        print("...erosion calculated")


    w.watermap = watermap(w,20000)
    w.irrigation = irrigation(w)
    w.humidity = humidity(w)
    hu_th = [
        ('low',find_threshold_f(w.humidity['data'],0.75,ocean)),
        ('med',find_threshold_f(w.humidity['data'],0.3,ocean)),
        ('hig',None)
    ]
    if verbose:
        print("...humidity calculated")

    # Temperature with thresholds
    t = temperature(i,e,ml)
    t_th = [
        ('vlo',find_threshold_f(t,0.87,ocean)),
        ('low',find_threshold_f(t,0.70,ocean)),
        ('med',find_threshold_f(t,0.30,ocean)),
        ('hig',None)
    ]
    w.set_temperature(t,t_th)
    
    # Permeability with thresholds
    perm = permeability(i)
    perm_th = [
        ('low',find_threshold_f(perm,0.75,ocean)),
        ('med',find_threshold_f(perm,0.25,ocean)),
        ('hig',None)
    ]
    w.set_permeability(perm,perm_th)

    if verbose:
        print("...permeability level calculated")    

    cm = {}
    biome_cm = {}
    biome = [[0 for x in xrange(WIDTH)] for y in xrange(HEIGHT)]
    for y in xrange(512):
        for x in xrange(512):
            if ocean[y][x]:
                biome[y][x] = 'ocean'
            else:
                el  = classify(e,e_th,x,y)
                hul = classify(w.humidity['data'],hu_th,x,y)          
                tl  = classify(t,t_th,x,y)
                pel = classify(perm,perm_th,x,y)
                complex_l = (el,hul,tl,pel)
                if not complex_l in cm:
                    cm[complex_l] = 0
                cm[complex_l] += 1
                if hul=='low' and tl=='low':
                    biome[y][x] = 'tundra'
                elif hul=='low' and tl=='hig':
                    biome[y][x] = 'sand desert'
                elif hul=='low' and tl=='med':
                    if pel=='low':
                        biome[y][x] = 'steppe'
                    else:
                        biome[y][x] = 'rock desert'
                elif hul=='hig' and tl=='hig':
                    biome[y][x] = 'jungle'
                elif hul=='hig' and pel=='low':
                    biome[y][x] = 'swamp'
                elif hul=='hig' and tl=='low':
                    biome[y][x] = 'forest'
                elif hul=='hig' and tl=='med':
                    biome[y][x] = 'forest'                  
                elif tl=='vlo':
                    biome[y][x] = 'iceland'
                elif hul=='med':
                    biome[y][x] = 'grassland'
                else:
                    biome[y][x] = 'UNASSIGNED'
            if not biome[y][x] in biome_cm:
                biome_cm[biome[y][x]] = 0
            biome_cm[biome[y][x]] += 1

    for cl in cm.keys():
        count = cm[cl]
        if verbose:
            print("%s = %i" %(str(cl),count))

    for cl in biome_cm.keys():
        count = biome_cm[cl]
        if verbose:
            print("%s = %i" %(str(cl),count))

    w.set_biome(biome)
    return w

