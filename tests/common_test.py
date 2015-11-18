import unittest
import numpy
from worldengine.common import Counter, anti_alias, get_verbose, set_verbose


class TestCommon(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_and_set_verbose(self):
        self.assertEqual(False, get_verbose(), "By default verbose should be set to False")
        set_verbose(True)
        self.assertEqual(True, get_verbose())
        set_verbose(False)
        self.assertEqual(False, get_verbose())

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
        self.assertAlmostEquals(1.2781818181818183, antialiased[0][0])
        self.assertAlmostEquals(0.4918181818181818, antialiased[1][2])

        original = numpy.array([[0.8]])
        antialiased = anti_alias(original, 10)
        self.assertAlmostEquals(0.8, antialiased[0][0])

if __name__ == '__main__':
    unittest.main()
