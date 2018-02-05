import unittest
from worldengine import main

class TestMyMain(unittest.TestCase):
    def test_main(self):
        arg_dict={"world_name":"test",
                    "width":50,
                    "height":50,
                    "seed":1,
                    "draw":False,
                    "save":False,
                    "operation":"world",
                    "generation_operation":True}
        main.main(None,arg_dict)
        
if __name__=="__main__":
    unittest.main()
