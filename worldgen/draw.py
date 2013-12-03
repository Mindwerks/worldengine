from PIL import Image

try:
	from worldgen.geo import WIDTH,HEIGHT,N_PLATES,MAX_ELEV
except:
	from geo import WIDTH,HEIGHT,N_PLATES,MAX_ELEV

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

def draw_elevation(world,filename):
	data = world.elevation['data']
	ocean = world.ocean
	img = Image.new('RGBA',(WIDTH,HEIGHT))
	pixels = img.load()
	#print(world.elevation['thresholds'].keys())
	sl = world.elevation['thresholds'][0][1]
	print("SL %i" % sl)
	for y in range(0,HEIGHT):
		for x in range(0,WIDTH):
			if ocean[y][x]:
				pixels[x,y] = (0,0,255,255)
			else:
				e = data[y][x]
				e_above_sl = int(e-sl+50)*2
				#print e
				if e_above_sl<0:
					pixels[x,y] = (255,255,255,255)
				elif e_above_sl>255:
					pixels[x,y] = (0,0,0,255)
				else:
					c = int(255-e_above_sl)
					pixels[x,y] = (c,c,c,255)
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


def draw_biome(temp,filename):	
	img = Image.new('RGBA',(WIDTH,HEIGHT))
	pixels = img.load()
	biome_colors = {
		'iceland': (208,241,245),
		'jungle' : (54,240,17),
		'tundra' : (147,158,157),
		'ocean'  : (23,94,145),
		'forest' : (10,89,15),
		'grassland' : (69,133,73),
		'steppe'    : (90,117,92),
		'sand desert' : (207,204,58),
		'rock desert' : (94,93,25)
	}
	for y in range(0,HEIGHT):
		for x in range(0,WIDTH):
			v = temp[y][x]
			pixels[x,y] = biome_colors[v]
	img.save(filename)	
