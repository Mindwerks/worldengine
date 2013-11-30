import random
import math

WIDTH  = 512
HEIGHT = 512
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
	random.seed(seed)

	# generate hot points
	hot_points = [random_point() for i in range(512)]

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

def elevnoise(elevation):
	from noise import pnoise2, snoise2
	octaves = 6
	freq = 16.0 * octaves
	for y in range(0,HEIGHT):
	    for x in range(0,WIDTH):
	    	n = int(snoise2(x / freq*2, y / freq*2, octaves) * 127.0 + 128.0)
	    	elevation[y][x]+=n/4

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
	elevnoise(elevation)

	return elevation

def draw_plates(plates,filename):
	from PIL import Image
	img = Image.new('RGBA',(WIDTH,HEIGHT))
	pixels = img.load()
	for y in range(0,HEIGHT):
		for x in range(0,WIDTH):
			n = plates[y][x]*255/N_PLATES
			pixels[x,y] = (n,n,n,255)
	img.save(filename)

def draw_elevation(elevation,filename):
	from PIL import Image
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

def find_elevation(elevation,land_perc):
	
	def count(e):
		tot = 0
		for y in range(0,HEIGHT):
			for x in range(0,WIDTH):
				if elevation[y][x]>e:
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
		print("For %i found %i (%f)" % (m,cm,float(cm)/(WIDTH*HEIGHT)))
		if desired<cm:
			return search(m,b,desired)
		else:
			return search(a,m,desired)

	desired_land = WIDTH*HEIGHT*land_perc
	print("Desired land: %i" % desired_land)
	return search(0,255,desired_land)

def draw_ocean_land(elevation,sea_level,filename):
	from PIL import Image
	img = Image.new('RGBA',(WIDTH,HEIGHT))
	pixels = img.load()
	for y in range(0,HEIGHT):
		for x in range(0,WIDTH):
			if elevation[y][x]>sea_level:
				pixels[x,y] = (0,255,0,255)
			else:
				pixels[x,y] = (0,0,255,255)
	img.save(filename)

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

def draw_land(elevation,ocean_map,hill_level,mountain_level,filename):
	from PIL import Image
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
	from PIL import Image
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
	from PIL import Image
	img = Image.new('RGBA',(WIDTH,HEIGHT))
	pixels = img.load()
	for y in range(0,HEIGHT):
		for x in range(0,WIDTH):
			c  = int(temp[y][x]*255)
			pixels[x,y] = (c,0,0,255)
	img.save(filename)	

def draw_precipitation(temp,filename):
	from PIL import Image
	img = Image.new('RGBA',(WIDTH,HEIGHT))
	pixels = img.load()
	for y in range(0,HEIGHT):
		for x in range(0,WIDTH):
			c  = int(temp[y][x]*255)
			pixels[x,y] = (0,0,c,255)
	img.save(filename)	


def temperature(seed):
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
			t = (latitude_factor*4+n)/5.0
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
			t = (latitude_factor*2+n)/3.0
			temp[y][x] = t

	return temp	