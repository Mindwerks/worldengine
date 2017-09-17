import unittest

import numpy

from worldengine.simulations.hydrology import WatermapSimulation
from worldengine.model.world import World, Size, GenerationParameters

class TestSimulation(unittest.TestCase):
    

    # The hydrology simulation indirectly calls the global rng.
    # We want different implementations of _watermap 
    # and internally called functions (especially random_land)
    # to show the same rng behaviour and not contamine the state of the global rng
    # should anyone else happen to rely on it.
    # This does only test that watermap leaves the rng in the state that the 
    # original implementation would have left it in and that a very small sample 
    # of results is the same as the original results.
    # It does not test if the implementation is actually correct. 
    # In fact it is hard to tell how "correctness" of a Monte Carlo process should
    # be judged.
    # Should it ever be decided that a "correct" implementation needs fewer or 
    # less calls to the rng, relative to the n parameter,
    # of course compatibility will be broken. 
    # Implicitly this is tested by the blessed images but it might be useful to
    # have a finer grained picture.

    def test_watermap_rng_stabilty(self):
        
        seed=12345
        numpy.random.seed(seed)

        size = Size(16,8)

        ocean = numpy.fromfunction(lambda y, x: y==x, (size.height, size.width))

        percipitation = numpy.ones((size.height, size.width))

        elevation = numpy.fromfunction(lambda y, x: y*x, (size.height, size.width))

        t = numpy.zeros(5)

        w = World("watermap",  size, seed, GenerationParameters(0, 1.0, 0))
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

        

if __name__ == '__main__':
    unittest.main()