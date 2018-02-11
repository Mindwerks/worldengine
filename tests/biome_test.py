import unittest
import numpy

from worldengine.simulations.biome import assign_biomes

class TestBiome(unittest.TestCase):

    def test_assign_biomes(self):
        temps=([1,1],[1,1])
        humids=numpy.array([[0.1,0.2],[0.15,0.05]])
        assign_biomes(temps,humids)

if __name__ == '__main__':
    unittest.main()
