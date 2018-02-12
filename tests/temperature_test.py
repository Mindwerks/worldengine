from worldengine.simulations.temperature import temper_sim
import unittest
import numpy

class TestMyTempSim(unittest.TestCase):
        
    def test_normal(self):
        el=numpy.array([[40,1],[0,2]])
        oc=numpy.array([[0,0],[1,0]])
        ml=1
        temper_sim(el,oc,ml)

if __name__=="__main__":
    unittest.main()

