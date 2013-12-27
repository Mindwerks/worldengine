from random import randint, choice, random
from app import db

import atomic
import math
from worldgen import geo

import sys
sys.modules['geo'] = geo

atomic.ATOMDIR = '.'

name_generator = atomic.Atomic()
name_generator.atomize('atoms/general')
name_generator.atomize('atoms/mages')
name_generator.atomize('atoms/fantasy')
name_generator.atomize('atoms/dwarves')
name_generator.atomize('atoms/hobbits')
name_generator.atomize('atoms/human_m')
name_generator.atomize('atoms/human_f')
name_generator.atomize('atoms/old_phoenix')

class Positioned:
	def __init__(self,x,y):
		self.x = x
		self.y = y

class Settlement(Positioned):	
	def __init__(self,x,y,name,type):
		"""Type should be Village, Town or City"""
		Positioned.__init__(self,x,y)
		self.name = name
		self.type = type

# Tiles:
# S Sea
# P Plain
# W Swamp
# M Mountain
# D Desert
# J Jungle
# F Forest
# H Hills

#online_users = mongo.db.users.find({'online': True})
#    return render_template('index.html',
#        online_users=online_users)

class WorldModel:
	def __init__(self,name,tiles,settlements):
		self.name   = name
		self.tiles  = tiles
		self.settlements = settlements

	def width(self):
		return len(self.tiles[0])

	def height(self):
		return len(self.tiles)

	def save(self):
		import pickle
		with open("worlds/world_%s.world" % self.name,'w') as f:
		    pickle.dump(self,f)

	@classmethod
	def load(self,name):
		import pickle
		with open("worlds/world_%s.world" % name,'r') as f:
		    return pickle.load(f)

	@classmethod
	def delete(self,name):
		path = "worlds/world_%s.world" % name
		import os
		os.remove(path)

	@classmethod
	def all_names(self):
		import os
		worlds_dir = 'worlds'
		names = []
		for dir_entry in os.listdir(worlds_dir):
			dir_entry_path = os.path.join(worlds_dir, dir_entry)
			if os.path.isfile(dir_entry_path) and dir_entry_path.endswith('.world'):
				name = os.path.splitext(dir_entry)[0]
				if name.startswith('world_'):
					name = name[len('world_'):]
					names.append(name)
		return names


class GameModel:
	def __init__(self,name,world):
		self.name   = name
		self.world  = world

	def save(self):
		import pickle
		with open("games/%s.game" % self.name,'w') as f:
		    pickle.dump(self,f)

	@classmethod
	def load(self,name):
		import pickle
		with open("games/%s.game" % name,'r') as f:
		    return pickle.load(f)

	@classmethod
	def get_or_404(self,name):
		return GameModel.load(name)

	@classmethod
	def delete(self,name):
		path = "worlds/%s.game" % name
		import os
		os.remove(path)

	@classmethod
	def all_names(self):
		import os
		worlds_dir = 'games'
		names = []
		for dir_entry in os.listdir(worlds_dir):
			dir_entry_path = os.path.join(worlds_dir, dir_entry)
			if os.path.isfile(dir_entry_path) and dir_entry_path.endswith('.game'):
				name = os.path.splitext(dir_entry)[0]
				names.append(name)
		return names


#class GameModel(db.Document):
#	name = db.StringField(max_length=255, required=True)
#	world_name = db.StringField(max_length=255, required=True)

#	def __init__(self,name,world_name):
#		self.name = name
#		self.world_name = world_name

class Adventurer(db.Document):
	name = db.StringField(max_length=255, required=True)
	race = db.StringField(max_length=255, required=True)
	job  = db.StringField(max_length=255, required=True)

	def __init__(self,race,job):
		self.race = race
		self.job = job

class Group(db.Document):
	name = db.StringField(max_length=255, required=True)
	

	def add_member(self,race,type):
		pass

def random_pos_centered_no_borders(w,h):
	minx = w/10+1
	maxx = (w*9)/10-1
	miny = h/10+1
	maxy = (h*9)/10-1
	x = randint(minx,maxx)
	y = randint(miny,maxy)
	return (x,y)

def random_pos_no_borders(w,h):
	x = randint(1,w-1)
	y = randint(1,h-1)
	return (x,y)

def random_land(w,h,tiles):
	x,y = random_pos_no_borders(w,h)
	if tiles[y][x]!='S':
		return (x,y)
	return random_land(w,h,tiles)

def random_plain(w,h,tiles):
	x,y = random_pos_no_borders(w,h)
	if tiles[y][x]=='P':
		return (x,y)
	return random_land(w,h,tiles)

def toward_center(x,w):
	pivot = w/2
	if x==pivot:
		return 0
	elif x<pivot:
		return 1
	else:
		return -1

def center_dist(x,w):
	pivot = w/2
	return abs(x-pivot)

def center_dist_prop(x,w):
	return float(center_dist(x,w))/float((w/2))

def move_in_borders(pos,w,h):
	x,y = pos
	x+=randint(-1,1)
	y+=randint(-1,1)
	if x==0:
		x=1
	if x>=(w-1):
		x=w-2
	if y==0:
		y=1
	if y>=(h-1):
		y=h-2
	return (x,y)		

def move_in_borders_towards_center(pos,w,h):
	x,y = pos
	p = center_dist_prop(x,w)
	if p<0.9 or random()<p:
		x+=randint(-1,1)
	else:
		x+=toward_center(x,w)
	p = center_dist_prop(y,h)
	if p<0.9 or random()<p:
		y+=randint(-1,1)
	else:
		y+=toward_center(y,h)
	if x==0:
		x=1
	if x>=(w-1):
		x=w-2
	if y==0:
		y=1
	if y>=(h-1):
		y=h-2
	return (x,y)

def move_in_land_with_inertia(pos,w,h,tiles,vector):
	if vector==None:
		vector = (0,0)
	vx,vy = vector
	nvector = (choice([vx,vx,vx,-1,0,1]),choice([vy,vy,vy,-1,0,1]))
	x,y = pos
	nvx,nvy = nvector
	nx = x+nvx
	ny = y+nvy
	#print("X %i Y %i NV %i,%i" % (x,y,nvx,nvy))
	if tiles[ny][nx]!='S':
		npos = (nx,ny)	
		return (npos,nvector)
	else:
		return move_in_land_with_inertia(pos,w,h,tiles,vector)

def move_in_land(pos,w,h,tiles):
	nvector = (choice([-1,0,1]),choice([-1,0,1]))
	x,y = pos
	nvx,nvy = nvector
	nx = x+nvx
	ny = y+nvy
	if tiles[ny][nx]!='S':	
		return (nx,ny)
	else:
		return move_in_land(pos,w,h,tiles)


def polish_name(name):
	vowels = 'aaeeiiouy'
	for i in range(0,len(name)-2):
		if (not name[i] in vowels) and (not name[i+1] in vowels) and (not name[i+2] in vowels):
			return polish_name(name[:i+2]+choice(vowels)+name[i+2:])
	return name

def generate_name():
	global name_generator
	name = name_generator.name()
	return polish_name(name).title()

def place_group(name,ntoplace,letter,ncurrent_lambda,tiles,w,h):
	print("%s to be placed %i" % (name,ntoplace))
	ncurrent = 0
	while ntoplace>0:
		if ncurrent==0:
			pos = random_plain(w,h,tiles)
			ncurrent = ncurrent_lambda()
		x,y = pos
		if tiles[y][x]=='P':
			tiles[y][x] = letter
			ntoplace-=1
		# ncurrent is reduced in every case, it avoids deadlocks
		ncurrent-=1
		pos = move_in_land(pos,w,h,tiles)
	return tiles

def in_border(x,y,w,h):
	return x>=0 and y>=0 and x<w and y<h

def settlements_around(tiles,x,y,w,h):
	for px in range(x-2,x+3):
		for py in range(y-2,y+3):
			if in_border(px,py,w,h) and tiles[py][px]=='C':
				return True
	return False

def create_map(w,h,worldname):
	print("Creating a world %ix%i" % (w,h))
	
	# All the tiles contain Sea
	tiles = [['S' for x in xrange(w)] for y in xrange(h)] 

	# Tiles usable for land are all but the borders:
	nborders = w*2+h*2-4
	nlandable = w*h-nborders
	print("Landable tiles %i" % nlandable)	
	nlandstoplace = randint(0,nlandable/5)+randint(0,nlandable/5)+randint(0,nlandable/5)
	nland = nlandstoplace
	sqnland = math.trunc(math.sqrt(nland))
	print("Land to be placed %i" % nlandstoplace)

	ncurrentcontinent = 0
	while nlandstoplace>0:
		if ncurrentcontinent==0:
			pos = random_pos_centered_no_borders(w,h)
			ncurrentcontinent= randint(2,10)*randint(1,nland/14)
		x,y = pos
		if tiles[y][x] == 'S':
			nlandstoplace-=1
			tiles[y][x] = 'P'
			ncurrentcontinent-=1
		pos = move_in_borders_towards_center(pos,w,h)

	# Place mountains
	vector = None
	ntoplace = randint(0,nland/9)+randint(0,nland/9)+randint(0,nland/9)
	print("Mountains to be placed %i" % ntoplace)
	ncurrent = 0
	while ntoplace>0:
		if ncurrent==0:
			pos = random_land(w,h,tiles)
			ncurrent = randint(1,sqnland/5)
		x,y = pos
		if tiles[y][x]!='M':
			tiles[y][x] = 'M'
			ntoplace-=1
		# current mountains is reduced in every case, it avoids deadlocks
		ncurrent-=1
		(pos,vector) = move_in_land_with_inertia(pos,w,h,tiles,vector)

	# Place hills	 
	tiles = place_group('Hills',randint(0,nland/9)+randint(0,nland/9)+randint(0,nland/9),
		'H',(lambda: randint(1,sqnland/5)),tiles,w,h)
	tiles = place_group('Deserts',randint(0,nland/11)+randint(0,nland/11),
		'D',(lambda: randint(1,sqnland/2)),tiles,w,h)
	tiles = place_group('Swamps',randint(0,nland/15)+randint(0,nland/15),
		'W',(lambda: randint(1,sqnland/10)),tiles,w,h)
	tiles = place_group('Jungles',randint(0,nland/15)+randint(0,nland/15),
		'J',(lambda: randint(1,sqnland/4)),tiles,w,h)
	tiles = place_group('Forests',randint(0,nland/7)+randint(0,nland/5),
		'F',(lambda: randint(1,sqnland/7)),tiles,w,h)

	# Place settlements
	nsettlements = randint(0,sqnland)+randint(0,sqnland)+randint(0,sqnland)
	settlements = []
	while nsettlements>0:
		x,y = random_land(w,h,tiles)
		if tiles[y][x]=='P' and not settlements_around(tiles,x,y,w,h):
			tiles[y][x] = 'C'
			name = generate_name()			
			if not [c for c in settlements if c.name==name]:
				type = choice(['village','village','village','town','town','city'])
				settlement = Settlement(x,y,name,type)
				settlements.append(settlement)
				nsettlements-=1

	world = World(worldname,tiles,settlements)
	return world

