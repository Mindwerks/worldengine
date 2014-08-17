import unittest
from lands.geo import *
from lands.plates import *
from lands.generator import *
import tempfile

class TestGeneration(unittest.TestCase):

    def setUp(self):
        pass

    def test_can_generate(self):
        w = world_gen("Dummy", 1, False, 100, 100, Step.get_by_name("full"))

    def test_serialization(self):
        w = world_gen("Dummy", 1, False, 10, 10, Step.get_by_name("full"))
        dumped = pickle.dumps(w, pickle.HIGHEST_PROTOCOL)
        loaded = pickle.loads(dumped)
        self.assertEquals(w, loaded)

    def test_serialization_on_file(self):
        fd, filename = tempfile.mkstemp()
        try:
            w = world_gen("Dummy", 1, False, 10, 10, Step.get_by_name("full"))
            with open(filename, "w") as f:
                pickle.dump(w, f, pickle.HIGHEST_PROTOCOL)
            with open(filename, "r") as f:
                loaded = pickle.load(f)
            self.assertEquals(w, loaded)
        finally:
            os.close(fd)
            os.remove(filename)

if __name__ == '__main__':
    unittest.main()