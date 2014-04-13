from basic import PositionedMixin, InGameMixin
import random
import math
import geo

class CulturalAdvancement():

    def __init__(self):
        self.merchant    = 0
        self.agriculture = 0
        self.naval       = 0
        self.weaponry    = 0
        self.government  = 0
        self.cultural    = 0

class Civilization(PositionedMixin,InGameMixin):

    def __init__(self,game,name,race,characteristics=None):
        self._game = game
        self._race  = race
        self.name = name
        self.settlements = []
        self.dead = False       
        if characteristics==None:
            characteristics = {}
            for ch in ['aggressiveness','war_power','governability','expansion_eagerness']:
                characteristics[ch] = (random.random()*0.30-0.15)+(random.random()*0.30-0.15)+getattr(race, ch)()
                if characteristics[ch]<0.01:
                    characteristics[ch] = 0.01
                elif characteristics[ch]>0.99:
                    characteristics[ch] = 0.99
        self.characteristics = characteristics

    def rank(self):
        if self.population()<10000:
            return 'tribe'
        elif self.population()<50000:
            return 'county'            
        elif self.population()<100000:
            return 'duchy'            
        elif self.population()<300000:
            return 'kingdom'
        else:
            return 'empire'                

    def aggressiveness(self):
        return self.characteristics['aggressiveness']

    def consider_secession(self):
        if len(self.alive_settlements())<2:
            return False
        if self.population()>self.maneagable_population() and random.random()>self.characteristics['governability']:
            return True
        return False

    def maneagable_population(self):
        v = int(10000**(0.5+self.characteristics['governability']))
        #print('Maneageable pop for %f %s: %i' % (self.characteristics['governability'],self.race().name(),v))
        return v

    def secession(self):
        new_characteristics = self.characteristics
        for ch in ['aggressiveness','war_power','governability','expansion_eagerness']:
            new_characteristics[ch] += random.random()*0.15
            if new_characteristics[ch]<0.01:
                new_characteristics[ch] = 0.01
            elif new_characteristics[ch]>0.99:
                new_characteristics[ch] = 0.99
        new_civ = Civilization(self._game,self.language.name(),self._race,new_characteristics)
        new_civ.language = self.language
        self.game().civilizations.append(new_civ)
        old_capital  = self.settlements[0]
        new_capital = random.choice(self.settlements[1:])
        new_civ.conquer_settlement(new_capital,self)
        for s in self.alive_settlements():
            if s!=old_capital and s!=new_capital:
                if geo.distance(s.position(),old_capital.position())>geo.distance(s.position(),new_capital.position()):
                    if random.random()<self.characteristics['governability']:
                        new_civ.conquer_settlement(s,self)

    def expansion_eagerness(self):
        return self.characteristics['expansion_eagerness']

    def expansion_distance(self):
        return int(6+self.expansion_eagerness()*6)

    def race(self):
        return self._race

    def game(self):
        return self._game

    def war_power(self):
        if self.population()<2:
            return 0.0
        pop = self.population()
        return self.characteristics['war_power']*(math.log(pop,1.05)*pop)/1000

    def conquer(self,other):
        other.dead = True
        self.game().log_event('%s conquered %s: getting %i settlements (he had %i)' % (self,other,len(other.alive_settlements()),len(self.alive_settlements())))
        for s in other.settlements:
            if not s.dead:
                s.civ = self
                self.settlements.append(s)

    def conquer_settlement(self,settlement,other):
        self.game().log_event('%s conquered %s from %s' % (self.name,settlement.name,other.name))
        settlement.civ = self
        self.settlements.append(settlement)
        other.settlements.remove(settlement)

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

    def sustainable_population(self,pos):
        return self.race().sustainable_population(self.game().world.biome_at(pos))

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
