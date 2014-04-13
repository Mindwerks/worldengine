import sys
sys.path.append("lands")

from langgen import *
import pickle
from geo import World
import geo
from civ import *
from civ.basic import *
from civ.events import *
from civ.draw import draw_civs
from civ.races import *
from civ.mechanic import *
from civ.civilizations import *
    
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
    for c in civs:
        print('\t%s of %s, settlements: %i' % (c.rank(),c.name,len(c.alive_settlements())))

def print_game_state(game):
    print('Turn %i, alive civilizations: %i' % (game.time,len(game.alive_civilizations())))
    print('=============================')
    for civ in game.alive_civilizations():
        print('[Civilization %s, %s (size:%i, land: %i, settlements: %i)]' % (civ.name,civ.race().name(),civ.population(),civ.land_size(),len(civ.alive_settlements())))
        for stlm in civ.alive_settlements():            
            print('\tSettlement %s: size %i, land %i (founded in %i)' % (stlm.name,stlm.size,stlm.land_size(),stlm.foundation))
    for r in [Human(),Orc(),Dwarf(),Elf()]:
        print_race_state(game,r)

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
    print('Usage:\n\tciv_simulator <world_path> <game_path> <ncvis> <turns> [seed]')
    sys.exit()

def main():
    if len(sys.argv)<5 or len(sys.argv)>6:
        usage()
    world_path = sys.argv[1]    
    game_path  = sys.argv[2]
    ncivs      = int(sys.argv[3])
    turns      = int(sys.argv[4])
    if len(sys.argv)==6:
        seed = int(sys.argv[5])
    else:
        random.seed()
        seed = random.randint(0,65536)
    random.seed(seed)
    print('Using seed %i to generate game %s in world "%s"' % (seed,game_path,world_path)) 

    world = pickle.load(open(world_path))

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

    game.save(game_path)

    draw_civs(game,'civs_%i.png' % (game.time))

#cProfile.run('main()')
main()
#print_game_state()

