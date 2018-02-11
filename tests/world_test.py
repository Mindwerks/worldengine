import numpy
import unittest
from worldengine.world import World

class TestWorld(unittest.TestCase): 
    def test_random_land_returns_only_land(self):
        size=(100,90)
        ocean = numpy.fromfunction(lambda y, x: y>=x, (size))
        
        w = World("random_land", 100,90, 1, 1, 1.0)
        
        w.ocean = ocean

        num_samples = 1000

        land_indices = w.random_land(num_samples)

        for i in range(0, num_samples*2, 2):
            self.assertFalse(ocean[land_indices[i+1],land_indices[i]])
        
if __name__=="__main__":
    unittest.main()
