#!/usr/bin/env python
"""
Part of the World Generator project. 

author:  Bret Curtis
license: LGPL v2

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
version 2 as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
02110-1301 USA
"""

class Path:

    def __init__( self, nodes, totalCost ):

        self.nodes = nodes
        self.totalCost = totalCost

    def getNodes( self ):
        return self.nodes

    def getTotalMoveCost( self ):
        return self.totalCost


class Node:

    def __init__( self, location, mCost, lid, parent = None ):
        self.location = location # where is this node located
        self.mCost = mCost  # total move cost to reach this node
        self.parent = parent # parent node
        self.score = 0 # calculated score for this node
        self.lid = lid # location id unique for each location in the map

    def __eq__( self, n ):
        if n.lid == self.lid:
            return 1
        else:
            return 0


class AStar:

    def __init__( self, maphandler ):
        self.mh = maphandler

    def _getBestOpenNode( self ):
        bestNode = None
        for n in self.on:
            if not bestNode:
                bestNode = n
            else:
                if n.score <= bestNode.score:
                    bestNode = n
        return bestNode

    def _tracePath( self, n ):
        nodes = []
        totalCost = n.mCost
        p = n.parent
        nodes.insert( 0, n )

        while 1:
            if p.parent is None:
                break

            nodes.insert( 0, p )
            p = p.parent

        return Path( nodes, totalCost )

    def _handleNode( self, node, end ):
        i = self.o.index( node.lid )
        self.on.pop( i )
        self.o.pop( i )
        self.c.append( node.lid )

        nodes = self.mh.getAdjacentNodes( node, end )

        for n in nodes:
            if n.location == end:
                # reached the destination
                return n
            elif n.lid in self.c:
                # already in close, skip this
                continue
            elif n.lid in self.o:
                # already in open, check if better score
                i = self.o.index( n.lid )
                on = self.on[i]
                if n.mCost < on.mCost:
                    self.on.pop( i )
                    self.o.pop( i )
                    self.on.append( n )
                    self.o.append( n.lid )
            else:
                # new node, append to open list
                self.on.append( n )
                self.o.append( n.lid )

        return None

    def findPath( self, fromlocation, tolocation ):
        self.o = []
        self.on = []
        self.c = []

        end = tolocation
        fnode = self.mh.getNode( fromlocation )
        if not fnode: # it is possible that fromLocation comes from mountain
            return None
        self.on.append( fnode )
        self.o.append( fnode.lid )
        nextNode = fnode

        # need to build in a bail-out counter
        counter = 0

        while nextNode is not None:
            if counter > 10000:
                break # no path found under limit
            finish = self._handleNode( nextNode, end )
            if finish:
                return self._tracePath( finish )
            nextNode = self._getBestOpenNode()
            counter += 1

        return None


class SQ_Location:
    """A simple Square Map Location implementation"""

    def __init__( self, x, y ):
        self.x = x
        self.y = y

    def __eq__( self, l ):
        if l.x == self.x and l.y == self.y:
            return 1
        else:
            return 0


class SQ_MapHandler:
    """A simple Square Map implementation"""

    def __init__( self, mapdata, width, height ):
        self.m = mapdata
        self.w = width
        self.h = height

    def getNode( self, location ):
        x = location.x
        y = location.y
        if x < 0 or x >= self.w or y < 0 or y >= self.h:
            return None
        d = self.m[( y * self.w ) + x]

#        import constants
#        if d >= ( constants.BIOME_ELEVATION_MOUNTAIN ): # not over mountains
#            return None

        return Node( location, d, ( ( y * self.w ) + x ) )

    def getAdjacentNodes( self, curnode, dest ):
        result = []

        cl = curnode.location
        dl = dest

        n = self._handleNode( cl.x + 1, cl.y, curnode, dl.x, dl.y )
        if n: result.append( n )
        n = self._handleNode( cl.x - 1, cl.y, curnode, dl.x, dl.y )
        if n: result.append( n )
        n = self._handleNode( cl.x, cl.y + 1, curnode, dl.x, dl.y )
        if n: result.append( n )
        n = self._handleNode( cl.x, cl.y - 1, curnode, dl.x, dl.y )
        if n: result.append( n )

        return result

    def _handleNode( self, x, y, fromnode, destx, desty ):
        n = self.getNode( SQ_Location( x, y ) )
        if n is not None:
            dx = max( x, destx ) - min( x, destx )
            dy = max( y, desty ) - min( y, desty )
            emCost = dx + dy
            n.mCost += fromnode.mCost
            n.score = n.mCost + emCost
            n.parent = fromnode
            #print dx,dy,emCost,fromnode.mCost,n.mCost,n.score
            return n

        return None


class pathFinder:
    '''Using the a* algo we will try to find the best path between two
    points'''
    def __init__( self ):
        pass

    def find( self, heightmap, source, destination ):
        sx, sy = source
        dx, dy = destination
        path = []
        dim = len( heightmap )

        # flatten array
        graph = heightmap.reshape( dim ** 2 )

        pathFinder = AStar( SQ_MapHandler( graph, dim, dim ) )
        start = SQ_Location( sx, sy )
        end = SQ_Location( dx, dy )

        #from time import time
        #s = time()
        p = pathFinder.findPath( start, end )
        #e = time()

        if not p:
            return path

        #print "      Found path in %d moves and %f seconds." % (len(p.nodes), (e-s))
        for node in p.nodes:
            path.append( [node.location.x, node.location.y] )

        return path