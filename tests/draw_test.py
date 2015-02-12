__author__ = 'Federico Tomassetti'

import unittest
import os
from PIL import Image
from lands.draw import _biome_colors, elevation_color, draw_simple_elevation_on_image
from lands.world import *

class TestDraw(unittest.TestCase):

    def setUp(self):
        tests_dir = os.path.dirname(os.path.realpath(__file__))
        self.tests_data_dir = os.path.abspath(os.path.join(tests_dir, './data'))
        self.tests_blessed_images_dir = os.path.abspath(os.path.join(tests_dir, './blessed_images'))


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

    def test_draw_simple_elevation_on_image(self):
        w = World.open_protobuf("%s/seed_28070.world" % self.tests_data_dir)
        data = w.elevation['data']
        drawn_img_pixels = draw_simple_elevation_on_image(data, w.width, w.height, w.sea_level()).load()
        blessed_img_pixels = Image.open("%s/elevation_28070.png" % self.tests_blessed_images_dir).load()

        for y in range(w.height):
            for x in range(w.width):
                blessed_pixel = blessed_img_pixels[x, y]
                drawn_pixel =  drawn_img_pixels[x, y]
                self.assertEqual(blessed_pixel, drawn_pixel, "Pixels at %i, %i are different. Blessed %s, drawn %s" % (x, y, blessed_pixel, drawn_pixel))

if __name__ == '__main__':
    unittest.main()
