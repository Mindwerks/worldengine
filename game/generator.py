from worldgen.namegen import *
import jsonpickle
from worldgen.geo import World
from worldgen import geo
from game.game import *
from game.events import *
from game.draw import draw_civs
    
#import cProfile
#import re

def print_game_state():
    print('Turn %i, alive civilizations: %i' % (game.time,len(game.alive_civilizations())))
    print('=============================')
    for civ in game.alive_civilizations():
        print('[Civilization %s (size:%i, land: %i, settlements: %i)]' % (civ.name,civ.population(),civ.land_size(),len(civ.alive_settlements())))
        for stlm in civ.alive_settlements():            
            print('Settlement %s: size %i, land %i (founded in %i)' % (stlm.name,stlm.size,stlm.land_size(),stlm.foundation))

def main():
    if len(sys.argv)!=5:
        usage()
    world_name = sys.argv[1]    
    game_name  = sys.argv[2]
    ncivs      = int(sys.argv[3])
    turns      = int(sys.argv[4])
    random.seed()
    seed = random.randint(0,65536)
    print('Using seed %i to add rivers & erosion to world "%s". Drops=%i' % (seed,world_name,drops)) 

    game = Game(world)

    with open('worlds/world_%s.json' % world_name, "r") as f:
        content = f.read()
    world = World.from_dict(jsonpickle.decode(content))

    for i in xrange(ncivs):    
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

    for i in xrange(1001):
        turn()
        print('[%i] Civs: %i, Population: %i, Settlements: %i, Land: %i, Wars: %i' % (game.time,len(game.alive_civilizations()),game.population(),len(game.alive_settlements()),game.land_size(),len(game.ongoing_wars())))
        #if i%50==0 and i>0:

    game.save(game_name)

    draw_civs(game,'%s_civs.png' % ('game',game.time))

#cProfile.run('main()')
main()
#print_game_state()

