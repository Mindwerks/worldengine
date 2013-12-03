from worldgen.namegen import *
import jsonpickle
from worldgen.geo import World
from worldgen import geo
from game.game import *
from game.events import *

with open('worlds/world_Normandy.json', "r") as f:
    content = f.read()
world = World.from_dict(jsonpickle.decode(content))
print('World %s' % world.name)

game = Game(world)

N_CIVS = 250

for i in xrange(N_CIVS):	
	language = generate_language()
	civilization = Civilization(game,language.name())
	civilization.language = language
	print(' ')
	print('Civilization %s' % civilization.name)
	print('--------------------------------------------')
	first_settlement = Settlement(civilization,world.random_land(),100)
	civilization.add_settlement(first_settlement)
	print('+ first settlement in %s, named %s' % (first_settlement.pos,first_settlement.name))
	x,y = first_settlement.pos
	print("\tbiome: %s" % world.biome[y][x])
	game.civilizations.append(civilization)
print(' ')
print(' ')
print('..start simulation')
print(' ')
print(' ')

def print_game_state():
	print('Turn %i, alive civilizations: %i' % (game.time,len(game.alive_civilizations())))
	print('=============================')
	for civ in game.alive_civilizations():
		print('[Civilization %s (size:%i, land: %i, settlements: %i)]' % (civ.name,civ.population(),civ.land_size(),len(civ.alive_settlements())))
		for stlm in civ.alive_settlements():			
			print('Settlement %s: size %i, land %i (founded in %i)' % (stlm.name,stlm.size,stlm.land_size(),stlm.foundation))


def turn(verbose=False):
	game.time += 1

	# check expansion
	events = []
	for i in xrange(50):
		events.append(Grow())
	for i in xrange(3):
		events.append(Famine())
	for i in xrange(1):
		events.append(Plague())				
	for civ in game.alive_civilizations():
		for stlm in civ.alive_settlements():			
			event = random.choice(events)
			rate = float(event.rate(crowded=stlm.crowded()))/100
			stlm.size = int(stlm.size*rate)
			if stlm.consider_disperding():
				if verbose:
					print('Settlment %s is dispersed' % stlm.name)
				if civ.disperse(stlm):
					if verbose:
						print('The civilization diseappears')
			if stlm.consider_expanding() and stlm.try_to_expand():
				if verbose:
					print('%s grew' % stlm.name)
			if stlm.consider_send_settlers():
				if stlm.try_to_send_settlers():
					if verbose:
						print('From settlment %s a new settlment is created' % stlm.name)
		for other in game.alive_civilizations():
			if other!=civ and (not civ.dead) and (not other.dead) and civ.distance_from_civ(other)<15:
				if (not civ.at_war_with(other)) and random.random()<0.05:
					game.start_war(civ,other)
					if verbose or True:
						print('[%i] Started war between %s and %s' % (game.time,civ.name,other.name))
	for w in game.ongoing_wars():
		w.proceed()

from game.draw import draw_civs
	
for i in xrange(501):
	turn()
	print('[%i] Civs: %i, Population: %i, Settlements: %i, Land: %i, Wars: %i' % (game.time,len(game.alive_civilizations()),game.population(),len(game.alive_settlements()),game.land_size(),len(game.ongoing_wars())))
	if i%100==0 and i>0:	
		draw_civs(game,'%s_civs_%i.png' % ('game',game.time))
#print_game_state()

