import unittest

import numpy

from worldengine.simulations.hydrology import watermap_sim#WatermapSimulation
#from worldengine.world import World

class TestSimulation(unittest.TestCase):
    
    #no longer true, the watermap does not involve rng anymore.
    
        # This does only test that watermap leaves the rng in the state that the 
        # original implementation would have left it in and that a very small sample 
        # of results is the same as the original results.
        # It does not test if the implementation is actually correct. 
        # In fact it is hard to tell how "correctness" of a Monte Carlo process should
        # be judged.
        # Should it ever be decided that a "correct" implementation needs fewer or 
        # more calls to the rng, relative to the n parameter,
        # of course compatibility will be broken. 
        # Implicitly this is tested by the blessed images but it might be useful to
        # have a finer grained picture.

    def test_watermap(self):#_rng_stabilty(self):
        seed=12345
        numpy.random.seed(seed)
        size=(16,8)
        ocean = numpy.fromfunction(lambda y, x: y==x, (size))
        precipitation = numpy.ones(size)
        elevation = numpy.fromfunction(lambda y, x: y*x, (size))
        watermap_sim(elevation,precipitation,ocean)   

if __name__ == '__main__':
    unittest.main()
