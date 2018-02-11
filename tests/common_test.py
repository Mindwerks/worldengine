import unittest
import numpy
from worldengine.common import Counter, anti_alias


class TestCommon(unittest.TestCase):

    def test_counter(self):
        c = Counter()
        self.assertEqual("", c.to_str())
        c.count("b")
        self.assertEqual("b : 1\n", c.to_str())
        c.count("b")
        c.count("b")
        self.assertEqual("b : 3\n", c.to_str())
        c.count("a")
        self.assertEqual("a : 1\nb : 3\n", c.to_str())

    def test_antialias(self):
        original = numpy.array([[0.5, 0.12, 0.7, 0.15, 0.0],
                                [0.0, 0.12, 0.7, 0.7, 8.0],
                                [0.2, 0.12, 0.7, 0.7, 4.0]])
        antialiased = anti_alias(original, 1)
        self.assertAlmostEqual(1.2781818181818183, antialiased[0][0])
        self.assertAlmostEqual(0.4918181818181818, antialiased[1][2])

        original = numpy.array([[0.8]])
        antialiased = anti_alias(original, 10)
        self.assertAlmostEqual(0.8, antialiased[0][0])
        
if __name__ == '__main__':
    unittest.main()
