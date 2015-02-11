__author__ = 'Federico Tomassetti'

import unittest
from lands.biome import *
from lands.draw import _biome_colors, elevation_color


class TestDraw(unittest.TestCase):

    def setUp(self):
        pass

    def test_biome_colors(self):
        self.assertEqual(Biome.all_names(), _biome_colors.keys().sort())

    def _assert_is_valid_color(self, color, color_name):
        r, g, b = color
        self.assertTrue(0.0 <= r <= 1.0, "red component %s is not in [0,1]: %f" % (color_name, r))
        self.assertTrue(0.0 <= g <= 1.0, "green component %s is not in [0,1]: %f" % (color_name, g))
        self.assertTrue(0.0 <= b <= 1.0, "blue component %s is not in [0,1]: %f" % (color_name, b))

    def test_elevation_color(self):
        for i in range(0, 20):
            v = i / 2.0
            c = ra, ga, ba = elevation_color(v)
            delta = 0.0000001
            c_low = rb, gb, bb = elevation_color(v - delta)
            c_high = rc, gc, bc = elevation_color(v + delta)

            # we want values to be in range
            self._assert_is_valid_color(c, "color for %f" % v)
            self._assert_is_valid_color(c_low, "color for %f (low)" % (v - delta))
            self._assert_is_valid_color(c_high, "color for %f (high)" % (v + delta))

            # we look for discontinuities
            # TODO verify this
            #self.assertAlmostEqual(ra, rb, 5, "value %f, red, low, from %f to %f" % (v, ra, rb))
            #self.assertAlmostEqual(ra, rc, 5, "value %f, red, high, from %f to %f" % (v, ra, rc))
            #self.assertAlmostEqual(ga, gb, 5, "value %f, green, low, from %f to %f" % (v, ga, gb))
            #self.assertAlmostEqual(ga, gc, 5, "value %f, green, high, from %f to %f" % (v, ga, gc))
            #self.assertAlmostEqual(ba, bb, 5, "value %f, blue, low, from %f to %f" % (v, ba, bb))
            #self.assertAlmostEqual(ba, bc, 5, "value %f, blue, high, from %f to %f" % (v, ba, bc))



if __name__ == '__main__':
    unittest.main()
