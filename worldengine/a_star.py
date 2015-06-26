#!/usr/bin/env python
"""
Part of the WorldEngine project.

author:  Bret Curtis
"""


class Path:
    def __init__(self, nodes, total_cost):
        self.nodes = nodes
        self.totalCost = total_cost

    def get_nodes(self):
        return self.nodes

    def get_total_movement_cost(self):
        return self.totalCost


class Node:
    def __init__(self, location, movement_cost, lid, parent=None):
        self.location = location  # where is this node located
        self.mCost = movement_cost  # total move cost to reach this node
        self.parent = parent  # parent node
        self.score = 0  # calculated score for this node
        self.lid = lid  # location id unique for each location in the map

    def __eq__(self, n):
        if n.lid == self.lid:
            return 1
        else:
            return 0


class AStar:
    def __init__(self, map_handler):
        self.mh = map_handler
        self.o = []
        self.on = []
        self.c = []

    def _get_best_open_node(self):
        best_node = None
        for n in self.on:
            if not best_node:
                best_node = n
            else:
                if n.score <= best_node.score:
                    best_node = n
        return best_node

    @staticmethod
    def _trace_path(n):
        nodes = []
        total_cost = n.mCost
        p = n.parent
        nodes.insert(0, n)

        while 1:
            if p.parent is None:
                break

            nodes.insert(0, p)
            p = p.parent

        return Path(nodes, total_cost)

    def _handle_node(self, node, end):
        i = self.o.index(node.lid)
        self.on.pop(i)
        self.o.pop(i)
        self.c.append(node.lid)

        nodes = self.mh.get_adjacent_nodes(node, end)

        for n in nodes:
            if n.location == end:
                # reached the destination
                return n
            elif n.lid in self.c:
                # already in close, skip this
                continue
            elif n.lid in self.o:
                # already in open, check if better score
                i = self.o.index(n.lid)
                on = self.on[i]
                if n.mCost < on.mCost:
                    self.on.pop(i)
                    self.o.pop(i)
                    self.on.append(n)
                    self.o.append(n.lid)
            else:
                # new node, append to open list
                self.on.append(n)
                self.o.append(n.lid)

        return None

    def find_path(self, from_location, to_location):
        end = to_location
        f_node = self.mh.get_node(from_location)
        if not f_node:  # it is possible that from_location comes from mountain
            return None
        self.on.append(f_node)
        self.o.append(f_node.lid)
        next_node = f_node

        # need to build in a bail-out counter
        counter = 0

        while next_node is not None:
            if counter > 10000:
                break  # no path found under limit
            finish = self._handle_node(next_node, end)
            if finish:
                return self._trace_path(finish)
            next_node = self._get_best_open_node()
            counter += 1

        return None


class SQLocation:
    """A simple Square Map Location implementation"""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, l):
        if l.x == self.x and l.y == self.y:
            return 1
        else:
            return 0


class SQMapHandler:
    """A simple Square Map implementation"""

    def __init__(self, map_data, width, height):
        self.m = map_data
        self.w = width
        self.h = height

    def get_node(self, location):
        x = location.x
        y = location.y
        if x < 0 or x >= self.w or y < 0 or y >= self.h:
            return None
        d = self.m[(y * self.w) + x]

        #        import constants
        #        if d >= ( constants.BIOME_ELEVATION_MOUNTAIN ): # not over mountains
        #            return None

        return Node(location, d, ((y * self.w) + x))

    def get_adjacent_nodes(self, cur_node, destination):
        result = []

        cl = cur_node.location
        dl = destination

        n = self._handle_node(cl.x + 1, cl.y, cur_node, dl.x, dl.y)
        if n:
            result.append(n)
        n = self._handle_node(cl.x - 1, cl.y, cur_node, dl.x, dl.y)
        if n:
            result.append(n)
        n = self._handle_node(cl.x, cl.y + 1, cur_node, dl.x, dl.y)
        if n:
            result.append(n)
        n = self._handle_node(cl.x, cl.y - 1, cur_node, dl.x, dl.y)
        if n:
            result.append(n)

        return result

    def _handle_node(self, x, y, from_node, destination_x, destination_y):
        n = self.get_node(SQLocation(x, y))
        if n is not None:
            dx = max(x, destination_x) - min(x, destination_x)
            dy = max(y, destination_y) - min(y, destination_y)
            em_cost = dx + dy
            n.mCost += from_node.mCost
            n.score = n.mCost + em_cost
            n.parent = from_node
            return n
        return None


def _matrix_to_array(matrix):
    array = []
    for row in matrix:
        for cell in row:
            array.append(cell)
    return array


class PathFinder:
    """Using the a* algorithm we will try to find the best path between two
       points"""

    def __init__(self):
        pass

    @staticmethod
    def find(heightmap, source, destination):
        sx, sy = source
        dx, dy = destination
        path = []
        dim = len(heightmap)

        # flatten array
        graph = _matrix_to_array(heightmap)

        pathfinder = AStar(SQMapHandler(graph, dim, dim))
        start = SQLocation(sx, sy)
        end = SQLocation(dx, dy)
        p = pathfinder.find_path(start, end)

        if not p:
            return path

        for node in p.nodes:
            path.append([node.location.x, node.location.y])

        return path
