from PIL import Image

try:
	from worldgen.geo import WIDTH,HEIGHT,N_PLATES,MAX_ELEV, antialias
except:
	from geo import WIDTH,HEIGHT,N_PLATES,MAX_ELEV, antialias

def draw_plates(plates,filename):
	
	img = Image.new('RGBA',(WIDTH,HEIGHT))
	pixels = img.load()
	for y in range(0,HEIGHT):
		for x in range(0,WIDTH):
			n = plates[y][x]*255/N_PLATES
			pixels[x,y] = (n,n,n,255)
	img.save(filename)

def draw_land_profile(elevation,sea_level,filename):
	
	img = Image.new('RGBA',(WIDTH,HEIGHT))
	pixels = img.load()
	for y in range(0,HEIGHT):
		for x in range(0,WIDTH):
			if elevation[y][x]>sea_level:
				pixels[x,y] = (0,255,0,255)
			else:
				pixels[x,y] = (0,0,255,255)
	img.save(filename)  

def draw_elevation(world,filename,shadow=True):
	data = world.elevation['data']
	ocean = world.ocean
	img = Image.new('RGBA',(WIDTH,HEIGHT))
	pixels = img.load()

	min_elev = None
	max_elev = None
	for y in xrange(HEIGHT):
		for x in xrange(WIDTH):
			if not ocean[y][x]:
				e = data[y][x]
				if min_elev==None or e<min_elev:
					min_elev=e
				if max_elev==None or e>max_elev:
					max_elev=e              
	elev_delta = max_elev-min_elev  

	for y in range(0,HEIGHT):
		for x in range(0,WIDTH):
			if ocean[y][x]:
				pixels[x,y] = (0,0,255,255)
			else:
				e = data[y][x]
				c = 255-int(((e-min_elev)*255)/elev_delta)
				if shadow and y>2 and x>2:
					if data[y-1][x-1]>e:
						c-=15
					if data[y-2][x-2]>e and data[y-2][x-2]>data[y-1][x-1]:
						c-=10       
					if data[y-3][x-3]>e and data[y-3][x-3]>data[y-1][x-1] and data[y-3][x-3]>data[y-2][x-2]:
						c-=5                                
					if c<0:
						c=0             
				pixels[x,y] = (c,c,c,255)
	img.save(filename)  

def draw_irrigation(world,filename):
	data  = world.irrigation
	ocean = world.ocean
	img   = Image.new('RGBA',(WIDTH,HEIGHT))
	pixels = img.load()

	min_elev = None
	max_elev = None
	for y in xrange(HEIGHT):
		for x in xrange(WIDTH):
			if not ocean[y][x]:
				e = data[y][x]
				if min_elev==None or e<min_elev:
					min_elev=e
				if max_elev==None or e>max_elev:
					max_elev=e              
	elev_delta = max_elev-min_elev  

	for y in range(0,HEIGHT):
		for x in range(0,WIDTH):
			if ocean[y][x]:
				pixels[x,y] = (0,0,255,255)
			else:
				e = data[y][x]
				c = int(((e-min_elev)*255)/elev_delta)      
				pixels[x,y] = (0,0,c,255)
	img.save(filename)

def draw_humidity(world,filename):
	ocean = world.ocean
	img   = Image.new('RGBA',(WIDTH,HEIGHT))
	pixels = img.load()

	min_elev = None
	max_elev = None
	for y in xrange(HEIGHT):
		for x in xrange(WIDTH):
			if not ocean[y][x]:
				e = world.humidity['data'][y][x]
				if min_elev==None or e<min_elev:
					min_elev=e
				if max_elev==None or e>max_elev:
					max_elev=e              
	elev_middle = world.humidity['quantiles']['50']
	elev_delta_plus = max_elev-elev_middle
	elev_delta_minus = elev_middle-min_elev 

	for y in range(0,HEIGHT):
		for x in range(0,WIDTH):
			if ocean[y][x]:
				pixels[x,y] = (0,0,255,255)
			else:
				e = world.humidity['data'][y][x]
				if e<elev_middle:
					c = int(((elev_middle-e)*255)/elev_delta_minus)     
					pixels[x,y] = (c,0,0,255)
				else:
					c = int(((e-elev_middle)*255)/elev_delta_plus)      
					pixels[x,y] = (0,c,0,255)

	img.save(filename)      


def draw_watermap(world, filename, th):
	ocean = world.ocean
	img = Image.new('RGBA',(WIDTH,HEIGHT))
	pixels = img.load()

	# min_elev = None
	# max_elev = None
	# for y in xrange(HEIGHT):
	#   for x in xrange(WIDTH):
	#       if not ocean[y][x]:
	#           e = _watermap[y][x]**1.5
	#           if min_elev==None or e<min_elev:
	#               min_elev=e
	#           if max_elev==None or e>max_elev:
	#               max_elev=e              
	# elev_delta = max_elev-min_elev    
	# if elev_delta<1:
	#   elev_delta=1

	for y in range(0,HEIGHT):
		for x in range(0,WIDTH):
			if ocean[y][x]:
				pixels[x,y] = (0,0,255,255)
			else:
				e = world.watermap[y][x]
				if e>th:
					c = 255
				else:
					c = 0
					#c = int(((e-min_elev)*255)/elev_delta)
				pixels[x,y] = (c,0,0,255)
	img.save(filename)  


def draw_basic_elevation(elevation,filename):
	img = Image.new('RGBA',(WIDTH,HEIGHT))
	pixels = img.load()
	for y in range(0,HEIGHT):
		for x in range(0,WIDTH):
			e = int(elevation[y][x]*255/MAX_ELEV)
			if e<0:
				e=0
			if e>255:
				e=255
			pixels[x,y] = (e,e,e,255)
	img.save(filename)

def draw_land(elevation,ocean_map,hill_level,mountain_level,filename):
	
	img = Image.new('RGBA',(WIDTH,HEIGHT))
	pixels = img.load()
	for y in range(0,HEIGHT):
		for x in range(0,WIDTH):
			if ocean_map[y][x]:
				pixels[x,y] = (0,0,255,255)
			elif elevation[y][x]>mountain_level:
				pixels[x,y] = (255,255,255,255)
			elif elevation[y][x]>hill_level:
				pixels[x,y] = (30,140,30,255)
			else:
				pixels[x,y] = (0,230,0,255)
				
	img.save(filename)  

def draw_ocean(ocean,filename): 
	img = Image.new('RGBA',(WIDTH,HEIGHT))
	pixels = img.load()
	for y in range(0,HEIGHT):
		for x in range(0,WIDTH):
			if ocean[y][x]:
				pixels[x,y] = (0,0,255,255)
			else:
				pixels[x,y] = (0,255,255,255)
	img.save(filename)  

def draw_temp(temp,filename):
	
	img = Image.new('RGBA',(WIDTH,HEIGHT))
	pixels = img.load()
	for y in range(0,HEIGHT):
		for x in range(0,WIDTH):
			c  = int(temp[y][x]*255)
			pixels[x,y] = (c,0,0,255)
	img.save(filename)  

def draw_precipitation(temp,filename):
	img = Image.new('RGBA',(WIDTH,HEIGHT))
	pixels = img.load()
	for y in range(0,HEIGHT):
		for x in range(0,WIDTH):
			c  = int(temp[y][x]*255)
			pixels[x,y] = (0,0,c,255)
	img.save(filename)  

def draw_sea(world,filename):
	img = Image.new('RGBA',(WIDTH,HEIGHT))

	pixels = img.load()
	for y in range(0,HEIGHT):
		for x in range(0,WIDTH):
			if world.is_land((x,y)):
				pixels[x,y] = (255,255,255,255)
			else:
				c = int(world.sea_depth[y][x]*200+50)
				pixels[x,y] = (0,0,255-c,255)
	img.save(filename)

class Counter:

	def __init__(self):
		self.c = {}

	def count(self,what):
		if not what in self.c:
			self.c[what] = 0
		self.c[what] +=1

	def printself(self):
		for w in self.c.keys():
			print("%s : %i" % (w,self.c[w]))

biome_colors = {
	'iceland': (208,241,245),
	'jungle' : (54,240,17),
	'tundra' : (180,120,130),
	'ocean'  : (23,94,145),
	'forest' : (10,89,15),
	'grassland' : (69,133,73),
	'steppe'    : (90,117,92),
	'sand desert' : (207,204,58),
	'rock desert' : (94,93,25),
	'swamp'       : (255,0,0),
	'glacier'	  : (255,255,255),
	'alpine'      : (100,70,5),
	'savanna'     : (200,140,20)
}


def draw_world(world,filename):
	img = Image.new('RGBA',(WIDTH,HEIGHT))

	counter = Counter()

	pixels = img.load()
	for y in range(0,HEIGHT):
		for x in range(0,WIDTH):
			if world.is_land((x,y)):
				biome = world.biome_at((x,y))
				pixels[x,y] = biome_colors[biome]	
			else:
				c = int(world.sea_depth[y][x]*200+50)
				pixels[x,y] = (0,0,255-c,255)

	counter.printself()
	img.save(filename)  

def draw_temperature_levels(world,filename):
	img = Image.new('RGBA',(WIDTH,HEIGHT))

	pixels = img.load()
	for y in range(0,HEIGHT):
		for x in range(0,WIDTH):
			if world.is_land((x,y)):
				e = world.elevation['data'][y][x]
				if world.is_temperature_very_low((x,y)):
					pixels[x,y] = (0,0,255,255)
				elif world.is_temperature_low((x,y)):
					pixels[x,y] = (80,120,255,255)
				elif world.is_temperature_medium((x,y)):
					pixels[x,y] = (180,255,180,255)
				elif world.is_temperature_high((x,y)):
					pixels[x,y] = (255,0,0,255)
			else:
				pixels[x,y] = (0,0,0,255)
	img.save(filename)  


def draw_biome(temp,filename):  
	img = Image.new('RGBA',(WIDTH,HEIGHT))
	pixels = img.load()
	biome_colors = {
		'iceland': (208,241,245),
		'jungle' : (54,240,17),
		'tundra' : (180,120,130),
		'ocean'  : (23,94,145),
		'forest' : (10,89,15),
		'grassland' : (69,133,73),
		'steppe'    : (90,117,92),
		'sand desert' : (207,204,58),
		'rock desert' : (94,93,25),
		'swamp'       : (255,0,0),
		'glacier'	  : (255,255,255),
		'alpine'      : (100,70,5),
		'savanna'     : (200,140,20)
	}

	for y in range(0,HEIGHT):
		for x in range(0,WIDTH):
			v = temp[y][x]
			pixels[x,y] = biome_colors[v]
	img.save(filename)  
