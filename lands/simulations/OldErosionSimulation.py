__author__ = 'Federico Tomassetti'

from lands.simulations.basic import *
import math

class ErosionSimulation(object):

    def is_applicable(self, world):
        return world.has_precipitations()

    def execute(self, world, seed):
        erosion_n = int((world.width * world.height * 3000000) / (512 * 512))
        self._erode(world, erosion_n)

    def _erode(self, world, n):
        EROSION_FACTOR = 250.0

        def droplet(world, pos, q, v):
            if q < 0:
                raise Exception('why?')
            x, y = pos
            pos_elev = world.elevation['data'][y][x]
            lowers = []
            min_higher = None
            min_lower = None
            tot_lowers = 0
            for p in world.tiles_around((x, y)):
                px, py = p
                e = world.elevation['data'][py][px]
                if e < pos_elev:
                    dq = int(pos_elev - e) << 2
                    if dq == 0:
                        dq = 1
                    lowers.append((dq, p))
                    tot_lowers += dq
                    if min_lower is None or e < min_lower:
                        min_lower = e
                else:
                    if min_higher is None or e > min_higher:
                        min_higher = e
            if lowers:
                f = q / tot_lowers
                for l in lowers:
                    s, p = l
                    if world.is_land(p):
                        px, py = p
                        ql = f * s
                        if ql < 0:
                            raise Exception('Why ql<0? f=%f s=%f' % (f, s))
                        # if ql<0.8*q:
                        # ql = q # rafforzativo
                        #ql = q
                        #going = world.elevation['data'][py][px]==min_higher
                        going = ql > 0.05
                        world.elevation['data'][py][px] -= ql / EROSION_FACTOR
                        if going:
                            droplet(world, p, ql, 0)
                            #elif random.random()<s:
                            #    droplet(world,p,ql,0)
            else:
                world.elevation['data'][y][x] += 0.3 / EROSION_FACTOR
                if world.elevation['data'][y][x] > min_higher:
                    world.elevation['data'][y][x] = min_higher
                    # world.elevation['data'][y][x] = min_higher

        for i in xrange(n):
            x, y = world.random_land()
            if True and world.precipitation['data'][y][x] > 0:
                droplet(world, (x, y), world.precipitation['data'][y][x] * 1, 0)
