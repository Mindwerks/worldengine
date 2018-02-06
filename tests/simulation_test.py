import unittest

import numpy

from worldengine.simulations.hydrology import WatermapSimulation
from worldengine.world import World

class TestSimulation(unittest.TestCase):

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

    def test_watermap_rng_stabilty(self):
        seed=12345
        numpy.random.seed(seed)

        size = (16,8)

        ocean = numpy.fromfunction(lambda y, x: y==x, (size))

        percipitation = numpy.ones(size)

        elevation = numpy.fromfunction(lambda y, x: y*x, (size))

        t = numpy.zeros(5)
        
        w = World("watermap", 16, 8, seed, 0, 1.0, 0)
        w.ocean = ocean
        w.precipitation = (percipitation, t)
        w.elevation = (elevation, t)

        d = numpy.random.randint(0,100)
        self.assertEqual(d, 98)

        data, t = WatermapSimulation._watermap(w, 200)

        self.assertAlmostEqual(data[4,4], 0.0)
        self.assertAlmostEqual(data[3,5], 4.20750776)

        d = numpy.random.randint(0,100)
        self.assertEqual(d, 59)


    def test_watermap_does_not_break_with_no_land(self):
        seed=12345
        numpy.random.seed(seed)

        size = (16,8)

        ocean = numpy.full(size, True, bool)

        w = World("watermap", 16, 8 , seed, 0, 1.0, 0)
        w.ocean = ocean

        data, t = WatermapSimulation._watermap(w, 200)


    def test_random_land_returns_only_land(self):
        size = (100,90)

        ocean = numpy.fromfunction(lambda y, x: y>=x, (size))
        
        w = World("random_land", 100,90, 0, 0, 1.0, 0)
        
        w.ocean = ocean

        num_samples = 1000

        land_indices = w.random_land(num_samples)

        for i in range(0, num_samples*2, 2):
            self.assertFalse(ocean[land_indices[i+1],land_indices[i]])
        

if __name__ == '__main__':
    unittest.main()
