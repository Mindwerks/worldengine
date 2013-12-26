from worldgen.namegen import *
import jsonpickle
import pickle
from worldgen.geo import World
from worldgen import geo
import random
import math
from events import *
from game.civilizations import *

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
    game.add_played_civ(civ)
    return game

class Game(object):

    def __init__(self,world):
        self.world = world
        self.civilizations = []
        self.time = 0
        self.wars = []
        self._occupied = {}     

    def set_played_civ(self,civ):
        self.civilizations.append(civ)
        self.played_civ = civ

    def rebuild_caches(self):
        self._occupied = {}
        for c in self.alive_civilizations():
            for s in c.alive_settlements():
                for p in s.positions():
                    self._occupied[p] = s

    def free_pos(self,pos):
        if pos in self._occupied:
            self._occupied.pop(pos)

    @classmethod
    def load(self,name):
        filename = 'games/%s.game' % name
        with open(filename, "r") as f:
            obj = pickle.load(f)
        return obj
    

    def save(self,name):
        filename = '%s.game' % name
        with open(filename, "w") as f:
            pickle.dump(self,f,pickle.HIGHEST_PROTOCOL)
    
    def add_ruin(self,settlement):
        pass

    def is_free_land(self,pos):
        return self.world.is_land(pos) and self.is_free(pos)

    def civ_owning(self,pos):
        for c in self.alive_civilizations():
            if c.occupy(pos):
                return c
        return None

    def host_settlement(self,pos):
        city = self.city_owning(self,pos)
        if city and city.position()==pos:
            return city
        else:
            return False

    def city_owning(self,pos):
        if pos in self._occupied:
            return self._occupied[pos]
        else:
            return None

    def is_free(self,pos):
        return not (pos in self._occupied)

    def alive_civilizations(self):
        return [c for c in self.civilizations if not c.dead]

    def population(self):
        tot = 0
        for c in self.alive_civilizations():
            tot += c.population()
        return tot

    def land_size(self):
        tot = 0
        for c in self.alive_civilizations():
            tot += c.land_size()
        return tot      

    def alive_settlements(self):
        l = []
        for c in self.alive_civilizations():
            l += c.alive_settlements()
        return l

    def ongoing_wars(self):
        return [w for w in self.wars if w.ongoing()]

    def war_between(self,a,b):
        for w in self.ongoing_wars():
            if w.between(a,b):
                return True
        return False

    def start_war(self,a,b):
        war = War([a,b])
        self.wars.append(war)

    def log_event(self,event):
        print("[%i] %s" % (self.time,event))

class InGameMixin:

    def game(self):
        raise Exception('To be implemented')

    def world(self):
        return self.game().world

class PositionedMixin:

    def positions(self):
        raise Exception('To implement')

    def distance(self,other_positioned):
        all_distances = []
        for pa in self.positions():
            for pb in other_positioned.positions():
                dist = geo.distance(pa,pb)
                all_distances.append(dist)
        return min(all_distances)

class War(InGameMixin):

    def __init__(self,civs):
        self.civs = civs
        self.start = self.game().time
        self.end = None
        self.scores = [0 for c in self.civs]

    def ongoing(self):
        return (self.end == None)

    def game(self):
        return self.civs[0].game()

    def finish(self):
        self.end = self.game().time

    def proceed(self):
        #self.game().log_event('..war between %s and %s is proceeding' % (self.civs[0],self.civs[1]))
        if self.civs[0].dead or self.civs[1].dead:
            self.finish()
            #self.game().log_event('..war between %s and %s finish because one civ died' % (self.civs[0],self.civs[1]))
        if self.try_peace():
            #self.game().log_event('..war between %s and %s ended with a truce' % (self.civs[0],self.civs[1]))
            self.finish()
        elif self.scores[0]>self.scores[1] and self.scores[0]>10*self.civs[1].war_power() and random.random()<0.3:
            #print('CONQUER %i vs %i' % (self.civs[0].population(),self.civs[1].population()))
            self.civs[0].conquer(self.civs[1])
            self.finish()
        elif self.scores[1]>self.scores[0] and self.scores[1]>10*self.civs[0].war_power() and random.random()<0.3:
            #print('CONQUER')           
            self.civs[1].conquer(self.civs[0])
            self.finish()
        else:           
            s1 = self.civs[0].war_power()*((random.random()+random.random()*2+2)/5)
            s2 = self.civs[1].war_power()*((random.random()+random.random()*2+2)/5)
            self.scores[0]+=s1
            self.scores[1]+=s2
            k1 = int(s2*0.3)
            k2 = int(s1*0.3)
            self.civs[0].kill(k1)
            self.civs[1].kill(k2)
            #self.game().log_event('..war between %s and %s is proceeding caused %i and %i killed' % (self.civs[0],self.civs[1],k1,k2))

    def try_peace(self):
        return random.random()<0.2;

    def between(self,a,b):
        return (a in self.civs) and (b in self.civs)


class Settlement(InGameMixin,PositionedMixin):

    def __init__(self,civ,pos,size,name=None):
        self.civ  = civ
        self.pos  = pos
        self.name = name
        if self.name==None:
            self.name = civ.language.name()
        self.size = size
        self.controlled_tiles = [pos]
        self.foundation = self.game().time
        self.dead = False
        self._occupy_cache = {}
        self._occupy_cache[pos]=True
        self.game()._occupied[pos] = self

    def sustainable_population(self):
        tot = 0
        for p in self.positions():
            tot += self.world().sustainable_population(p)
        return tot

    def position(self):
        return self.controlled_tiles[0]

    def distance_from_settlement(self,other):
        dist = geo.distance(self.position(),other.position())
        return dist

    def positions(self):
        return self.controlled_tiles

    def game(self):
        return self.civ.game()

    def land_size(self):
        return len(self.controlled_tiles)

    def try_to_expand(self):
        w = self.world()
        g = self.game()
        around = w.tiles_around_many(self.controlled_tiles,radius=1,predicate=g.is_free)
        if not around:
            return False
        else:
            around_with_sustainable = [(p,w.sustainable_population(p)) for p in around]
            around_with_sustainable.sort(key=lambda x: -1*x[1])
            new_pos,s = random.choice(around_with_sustainable[0:3])
            self.controlled_tiles.append(new_pos)
            self._occupy_cache[new_pos]=True
            self.game()._occupied[new_pos]=self
            return True

    def try_to_shrink(self):
        w = self.world()
        g = self.game()
        tiles = self.controlled_tiles[1:]
        tiles_with_sustainable = [(p,w.sustainable_population(p)/geo.distance(p,self.position())) for p in tiles]
        tiles_with_sustainable.sort(key=lambda x: -1*x[1])
        new_pos,s = random.choice(tiles_with_sustainable[0:3])
        self.controlled_tiles.remove(new_pos)
        self._occupy_cache[new_pos]=False
        self.game().free_pos(new_pos)
        return True

    def occupy(self,pos):
        #for t in self.controlled_tiles:
        #   if t==pos:
        #       return True
        #return False
        return pos in self._occupy_cache

    def crowded(self):
        return self.size>self.sustainable_population()

    def under_populated(self):
        return self.size<(self.sustainable_population()/10)

    def try_to_send_settlers(self):
        w = self.world()
        g = self.game()
        around = []
        for s in self.civ.alive_settlements():
            around += w.tiles_around(s.position(),radius=self.civ.expansion_distance(),predicate=g.is_free_land)
        if around:
            around_with_sustainable = [(p,w.sustainable_population(p)) for p in around]
            around_with_sustainable.sort(key=lambda x: -1*x[1])
            new_pos,s = random.choice(around_with_sustainable[0:len(around)/3+1])

            people_moving = random.randint(50,200)
            if people_moving>(self.size+100):
                people_moving = self.size+100               
            self.size -= people_moving
            new_settlment = Settlement(civ=self.civ,pos=new_pos,size=people_moving)
            self.civ.settlements.append(new_settlment)
            return True
        else:
            return False

    def consider_expanding(self):
        if self.crowded() and self.land_size()<=100:
            return random.random()<0.25
        else:
            return False

    def consider_shrinking(self):
        if self.under_populated() and self.land_size()>1:
            return random.random()<0.25
        else:
            return False

    def consider_disperding(self):
        return self.size<20 and random.random()<0.5

    def consider_send_settlers(self):
        return self.size>1000 and self.crowded() and random.random()<0.1*self.civ.expansion_eagerness()

    def consider_declaring_wars(self):
        wars = []       
        return wars

    def consider_secession(self):
        return False

    def population(self):
        return self.size

    def disperse(self):
        if self.dead:
            return      
        for p in self.controlled_tiles:
            self.game()._occupied.pop(p)
        self.civ.disperse(self)

    def kill(self,n):
        self.size -= n
        if self.size<0:
            self.size = 0
        if self.size==0:
            self.disperse()

def turn(game,verbose=False):
    game.time += 1

    if verbose:
        print("--- Turn %i ---" % game.time)

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
            old_size = stlm.size
            stlm.size = int(stlm.size*rate)
            if verbose:
                pass
                #print('Settlement %s went from %i to %i inhabitants' % (stlm.name,old_size,stlm.size))
            if stlm.consider_disperding():
                if verbose:
                    print('Settlment %s is dispersed' % stlm.name)
                if civ.disperse(stlm):
                    if verbose:
                        print('The civilization diseappears')
            if stlm.consider_expanding() and stlm.try_to_expand():
                if verbose:
                    print('%s grew to %i tiles' % (stlm.name,len(stlm.positions())))
            if stlm.consider_shrinking() and stlm.try_to_shrink():
                if verbose:
                    print('%s shrink to %i tiles' % (stlm.name,len(stlm.positions())))
            if stlm.consider_send_settlers():
                if stlm.try_to_send_settlers():
                    if verbose:
                        print('From settlment %s a new settlment is created' % stlm.name)
        for other in game.alive_civilizations():
            if other!=civ and (not civ.dead) and (not other.dead) and civ.distance_from_civ(other)<15:
                if (not civ.at_war_with(other)) and random.random()<(civ.aggressiveness()/10.0):
                    game.start_war(civ,other)
                    if verbose or True:
                        print('[%i] Started war between %s and %s' % (game.time,civ.name,other.name))
        if not civ.dead and civ.consider_secession():
            civ.secession()
    for w in game.ongoing_wars():
        w.proceed()
