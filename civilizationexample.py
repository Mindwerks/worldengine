from worldgen.namegen import *
import jsonpickle
from worldgen.geo import World

with open('worlds/world_Normandy.json', "r") as f:
    content = f.read()
world = World.from_dict(jsonpickle.decode(content))
print('World %s' % world.name)

class Settlement:

	def __init__(self,pos,name,size):
		self.pos = pos
		self.name = name
		self.size = size


class Civilization:

	def __init__(self,name):
		self.name = name
		self.settlements = []

	def add_settlement(self,settlement):
		self.settlements.append(settlement)

	def disperse(self,settlement):
		self.settlements.remove(settlement)
		if len(self.settlements)==0:
			

civilizations = []
for i in xrange(10):	
	language = generate_language()
	civilization = Civilization(language.name())
	civilization.language = language
	print(' ')
	print('Civilization %s' % civilization.name)
	print('--------------------------------------------')
	first_settlement = Settlement(world.random_land(),language.name(),100)
	civilization.add_settlement(first_settlement)
	print('+ first settlement in %s, named %s' % (first_settlement.pos,first_settlement.name))
	x,y = first_settlement.pos
	print("\tbiome: %s" % world.biome[y][x])
	civilizations.append(civilization)

time = 0

class Event:
	
	def rate(self):
		return random.randint(self.min,self.max)

class Plague(Event):

	def __init__(self):
		self.min = 20
		self.max = 90

class Famine(Event):

	def __init__(self):
		self.min = 80
		self.max = 90

class Grow(Event):

	def __init__(self):
		self.min = 101
		self.max = 105

def turn():
	global time
	time += 1
	print(' ')
	print('Turn %i' % time)
	print('=============================')
	# check expansion
	events = []
	for i in xrange(50):
		events.append(Grow())
	for i in xrange(3):
		events.append(Famine())
	for i in xrange(1):
		events.append(Plague())				
	for civ in civilizations:
		print('[Civilization %s]' % civ.name)
		for stlm in civ.settlements:			
			event = random.choice(events)
			rate = float(event.rate())/100
			stlm.size = int(stlm.size*rate)
			if stlm.size<20 and random.random()<0.5:
				print('Settlment %s is dispersed' % stlm.name)
				civ.disperse(stlm)
			if stlm.size>500 and random.random()<0.1:
				print('From settlment %s a new settlment is created' % stlm.name)				
			print('Settlement %s: size %i' % (stlm.name,stlm.size))
		print(' ')
for i in xrange(100):
	turn()