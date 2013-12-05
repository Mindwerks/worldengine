from worldgen.namegen import *
import jsonpickle
from worldgen.geo import World
from worldgen import geo
import random
import math

class Game:

    def __init__(self,world):
        self.world = world
        self.civilizations = []
        self.time = 0
        self.wars = []
        self._occupied = {}     

    def add_ruin(self,settlement):
        pass

    def is_free_land(self,pos):
        return self.world.is_land(pos) and self.is_free(pos)

    def civ_owning(self,pos):
        for c in self.alive_civilizations():
            if c.occupy(pos):
                return c
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
        elif self.scores[0]>self.scores[1] and self.scores[0]>10*self.civs[1].strength() and random.random()<0.3:
            #print('CONQUER %i vs %i' % (self.civs[0].population(),self.civs[1].population()))
            self.civs[0].conquer(self.civs[1])
            self.finish()
        elif self.scores[1]>self.scores[0] and self.scores[1]>10*self.civs[0].strength() and random.random()<0.3:
            #print('CONQUER')           
            self.civs[1].conquer(self.civs[0])
            self.finish()
        else:           
            s1 = self.civs[0].strength()*((random.random()+random.random()*2+2)/5)
            s2 = self.civs[1].strength()*((random.random()+random.random()*2+2)/5)
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
        self.game()._occupied[pos] = True

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
            self.game()._occupied[new_pos]=True
            return True

    def occupy(self,pos):
        #for t in self.controlled_tiles:
        #   if t==pos:
        #       return True
        #return False
        return pos in self._occupy_cache

    def crowded(self):
        return self.size>self.sustainable_population()

    def try_to_send_settlers(self):
        w = self.world()
        g = self.game()
        around = []
        for s in self.civ.alive_settlements():
            around += w.tiles_around(s.position(),radius=15,predicate=g.is_free_land)
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

    def consider_disperding(self):
        return self.size<20 and random.random()<0.5

    def consider_send_settlers(self):
        return self.size>1000 and (self.size/self.land_size())>700 and random.random()<0.05

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

class Civilization(PositionedMixin,InGameMixin):

    def __init__(self,game,name):
        self._game = game
        self.name = name
        self.settlements = []
        self.dead = False

    def game(self):
        return self._game

    def strength(self):
        if self.population()<2:
            return 0.0
        pop = self.population()
        return (math.log(pop,1.05)*pop)/1000

    def conquer(self,other):
        other.dead = True
        self.game().log_event('%s conquered %s: getting %i settlements (he had %i)' % (self,other,len(other.alive_settlements()),len(self.alive_settlements())))
        for s in other.settlements:
            if not s.dead:
                s.civ = self
                self.settlements.append(s)

    def positions(self):
        ps = []
        for s in self.alive_settlements():
            ps = ps + s.positions()
        return ps

    def distance_from_civ(self,other):
        min_dist = None
        for s1 in self.alive_settlements():
            for s2 in other.alive_settlements():
                dist = s1.distance_from_settlement(s2)
                if min_dist==None or min_dist>dist:
                    min_dist=dist
        return min_dist

    def add_settlement(self,settlement):
        self.settlements.append(settlement)

    def alive_settlements(self):
        #return [s for s in self.settlements if not s.dead]
        return self.settlements

    def disperse(self,settlement):
        settlement.dead = True
        settlement.size = 0
        self.settlements.remove(settlement)
        self.game().add_ruin(settlement)
        if len(self.alive_settlements())==0:
            self.dead = True
        return self.dead

    def occupy(self,pos):
        for s in self.alive_settlements():
            if s.occupy(pos):
                return True
        return False

    def population(self):
        t = 0
        for s in self.alive_settlements():
            t+=s.size
        return t

    def land_size(self):
        t = 0
        for s in self.alive_settlements():
            t+=s.land_size()
        return t

    def at_war_with(self,other):
        return self.game().war_between(self,other)

    def kill(self,n,pool=None):
        start_n = n
        if not self.alive_settlements():
            return
        if self.population()<0:
            raise Exception('Error!')
        if n>=self.population():
            for s in self.alive_settlements():
                s.disperse()
            return
        cap = 1000
        if n>1000000:
            cap = 35000
        elif n>100000:
            cap = 15000
        elif n>20000:
            cap = 5000

        if pool==None:
            pool = []
            for s in self.alive_settlements():
                for i in xrange((s.population()/cap) +1):
                    pool.append(s)
        r = random.randint(cap/3,cap)
        if r>n:
            r = n
        s = random.choice(pool)
        if r>s.population():
            n += (r-s.population())
            if not s.dead:
                pool=None
                s.disperse()
        else:
            s.kill(r)
        n -= r
        if n>0:
            if n>start_n:
                raise Exception('...it should not happen')
            elif n==start_n:
                # avoid deadlocks...
                n -= random.randint(0,10)
            self.kill(n,pool)

    def __repr__(self):
        return "Civ %s" % self.name
