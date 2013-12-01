import random
import math
from noise import snoise2

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
			if elevation[y][x]<mountain_level:
				altitude_factor = 0.5
			else:
				altitude_factor = 1.0-float(elevation[y][x]-mountain_level)/(255-mountain_level)

			n = snoise2(x / freq, y / freq, octaves,base=base)
			t = (latitude_factor*2+n*2+altitude_factor*3)/7.0
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
			t = (latitude_factor+n*2)/3.0
			temp[y][x] = t

	return temp

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
		#instance.set_permeability(map_from_dict(dict['permeability']['data']),[])
		return instance


def world_gen(name,seed,verbose=False):
	plates = generate_plates(seed)
	e = generate_base_heightmap(seed,plates)
	w = world_gen_from_elevation(name,e,seed,verbose=verbose)
	return w

def world_gen_from_elevation(name,elevation,seed,verbose=False):
	i = seed
	w = World(name)

	# Elevation with thresholds
	e = elevation
	sl = find_threshold(e,0.3)
	ocean = fill_ocean(e,sl+1.5)
	hl = find_threshold(e,0.10)
	ml = find_threshold(e,0.03)
	e_th = [('plain',hl),('hill',ml),('mountain',None)]
	w.set_ocean(ocean)
	w.set_elevation(e,e_th)

	# Precipitation with thresholds
	p = precipitation(i)
	p_th = [
		('low',find_threshold_f(p,0.75,ocean)),
		('med',find_threshold_f(p,0.3,ocean)),
		('hig',None)
	]
	w.set_precipitation(p,p_th)

	# Temperature with thresholds
	t = temperature(i,e,ml)
	t_th = [
		('vlo',find_threshold_f(t,0.95,ocean)),
		('low',find_threshold_f(t,0.75,ocean)),
		('med',find_threshold_f(t,0.4,ocean)),
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

	cm = {}
	biome_cm = {}
	biome = [[0 for x in xrange(WIDTH)] for y in xrange(HEIGHT)]
	for y in xrange(512):
		for x in xrange(512):
			if ocean[y][x]:
				biome[y][x] = 'ocean'
			else:
				el = classify(e,e_th,x,y)
				prl = classify(p,p_th,x,y)			
				tl = classify(t,t_th,x,y)
				pel = classify(perm,perm_th,x,y)
				complex_l = (el,prl,tl,pel)
				if not complex_l in cm:
					cm[complex_l] = 0
				cm[complex_l] += 1
				if prl=='low' and tl=='low':
					biome[y][x] = 'tundra'
				elif prl=='low' and tl=='hig':
					biome[y][x] = 'sand desert'
				elif prl=='low' and tl=='med':
					if pel=='low' or pel=='med':
						biome[y][x] = 'steppe'
					else:
						biome[y][x] = 'rock desert'
				elif prl=='hig' and tl=='hig':
					biome[y][x] = 'jungle'
				elif prl=='hig' and prl=='low':
					biome[y][x] = 'swamp'
				elif prl=='hig' and tl=='low':
					biome[y][x] = 'forest'
				elif prl=='hig' and tl=='med':
					biome[y][x] = 'forest'					
				elif tl=='vlo':
					biome[y][x] = 'iceland'
				elif prl=='med':
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

