from civilizations import Civilization
from basic import Game, generate_language, Settlement
import random

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
    first_settlement = Settlement(civilization,find_start_location(civilization,game),100)
    civilization.add_settlement(first_settlement)
    x,y = first_settlement.pos
    return civilization

def start_game(world,name,race):
    game = Game(world)
    game.name = name
    civ = generate_civ(race=race,game=game)
    game.set_played_civ(civ)
    return game