from worldgen.namegen import *
import jsonpickle
from worldgen.geo import World
from worldgen import geo
from game.game import *
from game.events import *
from game.draw import draw_civs
from game.races import *
from game.civilizations import *
import sys
    
#import cProfile
#import re

def print_race_state(game,race):
    civs = []
    land = 0
    pop = 0
    for civ in game.alive_civilizations():
        if civ.race().name()==race.name():
            civs.append(civ)
            land += civ.land_size()
            pop += civ.population()
    print('## %s civs %i ##' % (race.name(),len(civs)))
    print('\tland size: %i' % land)
    print('\tpeople: %i' % pop)

def print_game_state(game):
    print('Turn %i, alive civilizations: %i' % (game.time,len(game.alive_civilizations())))
    print('=============================')
    for civ in game.alive_civilizations():
        print('[Civilization %s, %s (size:%i, land: %i, settlements: %i)]' % (civ.name,civ.race().name(),civ.population(),civ.land_size(),len(civ.alive_settlements())))
        for stlm in civ.alive_settlements():            
            print('\tSettlement %s: size %i, land %i (founded in %i)' % (stlm.name,stlm.size,stlm.land_size(),stlm.foundation))
    for r in [Human(),Orc(),Dwarf(),Elf()]:
        print_race_state(game,r)

def find_start_location(civ,game):
    pos=None
    while pos==None or not game.is_free(pos):
        pos = game.world.random_land()
        if random.random()>=float(civ.sustainable_population(pos)/1000.0):
            pos=None
    return pos

def generate_civ(game,race):
    language = generate_language()
    civilization = Civilization(game,language.name(),race)        
    civilization.language = language
    print(' ')
    print('Civilization %s, race %s' % (civilization.name,civilization.race().name()))
    print('--------------------------------------------')
    first_settlement = Settlement(civilization,find_start_location(civilization,game),100)
    civilization.add_settlement(first_settlement)
    print('+ first settlement in %s, named %s' % (first_settlement.pos,first_settlement.name))
    x,y = first_settlement.pos
    print("\tbiome: %s" % game.world.biome[y][x])
    game.civilizations.append(civilization)

def usage():
    print('Missing params')

def main():
    if len(sys.argv)!=5:
        usage()
    world_name = sys.argv[1]    
    game_name  = sys.argv[2]
    ncivs      = int(sys.argv[3])
    turns      = int(sys.argv[4])
    random.seed()
    seed = random.randint(0,65536)
    print('Using seed %i to generate game %s in world "%s"' % (seed,game_name,world_name)) 

    with open('worlds/world_%s.json' % world_name, "r") as f:
        content = f.read()
    world = World.from_dict(jsonpickle.decode(content))

    game = Game(world)

    for i in xrange(ncivs):    
        generate_civ(game,Dwarf())
    
    for i in xrange(ncivs):    
        generate_civ(game,Elf())

    for i in xrange(ncivs):    
        generate_civ(game,Orc())        

    for i in xrange(ncivs):    
        generate_civ(game,Human())

    print(' ')
    print(' ')
    print('..start simulation')
    print(' ')
    print(' ')

    for i in xrange(turns):
        turn(game,verbose=True)
        print('[%i] Civs: %i, Population: %i, Settlements: %i, Land: %i, Wars: %i' % (game.time,len(game.alive_civilizations()),game.population(),len(game.alive_settlements()),game.land_size(),len(game.ongoing_wars())))
        if (i+1)%50==0 and i>1:
            print_game_state(game)

    game.save(game_name)

    draw_civs(game,'%s_civs_%i.png' % (game_name,game.time))

#cProfile.run('main()')
main()
#print_game_state()

