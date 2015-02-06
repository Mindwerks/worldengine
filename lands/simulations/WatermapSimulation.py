__author__ = 'Federico Tomassetti'

from lands.simulations.basic import *

class WatermapSimulation(object):

    def is_applicable(self, world):
        return world.has_precipitations() and (not world.has_watermap())

    def execute(self, world, seed):
        world.watermap = self._watermap(world, 20000)


    def _watermap(self, world, n):
        def droplet(world, pos, q, _watermap):
            if q < 0:
                return
            x, y = pos
            pos_elev = world.elevation['data'][y][x] + _watermap[y][x]
            lowers = []
            min_higher = None
            min_lower = None
            pos_min_higher = None
            tot_lowers = 0
            for p in world.tiles_around((x, y)):
                px, py = p
                e = world.elevation['data'][py][px] + _watermap[py][px]
                if e < pos_elev:
                    dq = int(pos_elev - e) << 2
                    if min_lower == None or e < min_lower:
                        min_lower = e
                        if dq == 0:
                            dq = 1
                    lowers.append((dq, p))
                    tot_lowers += dq

                else:
                    if min_higher == None or e > min_higher:
                        min_higher = e
                        pos_min_higher = p
            if lowers:
                f = q / tot_lowers
                for l in lowers:
                    s, p = l
                    if world.is_land(p):
                        px, py = p
                        ql = f * s
                        # ql = q
                        going = ql > 0.05
                        _watermap[py][px] += ql
                        if going:
                            droplet(world, p, ql, _watermap)
            else:
                _watermap[y][x] += q

        _watermap_data = [[0 for x in xrange(world.width)] for y in xrange(world.height)]
        for i in xrange(n):
            x, y = world.random_land()
            if True and world.precipitation['data'][y][x] > 0:
                droplet(world, (x, y), world.precipitation['data'][y][x], _watermap_data)
        _watermap = {'data': _watermap_data}
        _watermap['thresholds'] = {}
        _watermap['thresholds']['creek'] = find_threshold_f(_watermap_data, 0.05, ocean=world.ocean)
        _watermap['thresholds']['river'] = find_threshold_f(_watermap_data, 0.02, ocean=world.ocean)
        _watermap['thresholds']['main river'] = find_threshold_f(_watermap_data, 0.007, ocean=world.ocean)
        return _watermap
