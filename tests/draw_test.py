import unittest
import os
from worldengine.draw import _biome_colors, Image, draw_simple_elevation, elevation_color, \
    draw_elevation, draw_riversmap, draw_grayscale_heightmap, draw_ocean, draw_precipitation, \
    draw_world, draw_temperature_levels, draw_biome
from worldengine.biome import Biome
from worldengine.world import World


class PixelCollector:

    def __init__(self, width, height):
        self.pixels = {}
        self.width = width
        self.height = height
        for y in range(height):
            for x in range(width):
                self.pixels[x, y] = (0, 0, 0, 0)

    def set_pixel(self, x, y, color):
        if len(color) == 3:
            color = color + (255,)
        self.pixels[(x, y)] = color

    def __getitem__(self, item):
        return self.pixels[item]

    def __setitem__(self, key, value):
        self.pixels[key] = value


class TestBase(unittest.TestCase):

    def setUp(self):
        tests_dir = os.path.dirname(os.path.realpath(__file__))
        self.tests_data_dir = os.path.abspath(os.path.join(
            tests_dir, "../../worldengine-data/tests/data"))
        self.tests_blessed_images_dir = os.path.abspath(
            os.path.join(tests_dir, "../../worldengine-data/tests/images"))
        self.assertTrue(
            os.path.isdir(self.tests_data_dir),
            "worldengine-data doesn't exist, please clone it before continuing.")

    def _assert_is_valid_color(self, color, color_name):
        r, g, b = color
        self.assertTrue(0.0 <= r <= 1.0, "red component %s is not in [0,1]: %f" % (color_name, r))
        self.assertTrue(0.0 <= g <= 1.0, "green component %s is not in [0,1]: %f" % (color_name, g))
        self.assertTrue(0.0 <= b <= 1.0, "blue component %s is not in [0,1]: %f" % (color_name, b))

    def _assert_are_colors_equal(self, expected, actual):
        if len(expected) == 3:
            expected = expected + (255,)
        if len(actual) == 3:
            actual = actual + (255,)
        self.assertEqual(expected, actual)

    def _assert_img_equal(self, blessed_image_name, drawn_image):
        blessed_img = Image.open("%s/%s.png" % (self.tests_blessed_images_dir, blessed_image_name))
        blessed_img_pixels = blessed_img.load()

        blessed_img_width, blessed_img_height = blessed_img.size
        self.assertEqual(blessed_img_width, drawn_image.width)
        self.assertEqual(blessed_img_height, drawn_image.height)
        for y in range(blessed_img_height):
            for x in range(blessed_img_width):
                blessed_pixel = blessed_img_pixels[x, y]
                drawn_pixel = drawn_image[x, y]
                self.assertEqual(blessed_pixel, drawn_pixel,
                                 "Pixels at %i, %i are different. Blessed %s, drawn %s"
                                 % (x, y, blessed_pixel, drawn_pixel))


class TestDraw(TestBase):

    def setUp(self):
        super(TestDraw, self).setUp()

    def test_biome_colors(self):
        self.assertEqual(Biome.all_names(), _biome_colors.keys().sort())

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

    def test_draw_simple_elevation(self):
        w = World.open_protobuf("%s/seed_28070.world" % self.tests_data_dir)
        data = w.elevation['data']
        target = PixelCollector(w.width, w.height)
        draw_simple_elevation(data, w.width, w.height, w.sea_level(), target)
        self._assert_img_equal("simple_elevation_28070", target)

    def test_draw_elevation_shadow(self):
        w = World.open_protobuf("%s/seed_28070.world" % self.tests_data_dir)
        data = w.elevation['data']
        target = PixelCollector(w.width, w.height)
        draw_elevation(w, True, target)
        self._assert_img_equal("elevation_28070_shadow", target)

    def test_draw_elevation_no_shadow(self):
        w = World.open_protobuf("%s/seed_28070.world" % self.tests_data_dir)
        data = w.elevation['data']
        target = PixelCollector(w.width, w.height)
        draw_elevation(w, False, target)
        self._assert_img_equal("elevation_28070_no_shadow", target)

    def test_draw_river_map(self):
        w = World.open_protobuf("%s/seed_28070.world" % self.tests_data_dir)
        target = PixelCollector(w.width, w.height)
        draw_riversmap(w, target)
        self._assert_img_equal("riversmap_28070", target)

    def test_draw_grayscale_heightmap(self):
        w = World.open_protobuf("%s/seed_28070.world" % self.tests_data_dir)
        target = PixelCollector(w.width, w.height)
        draw_grayscale_heightmap(w, target)
        self._assert_img_equal("grayscale_heightmap_28070", target)

    def test_draw_ocean(self):
        w = World.open_protobuf("%s/seed_28070.world" % self.tests_data_dir)
        target = PixelCollector(w.width, w.height)
        draw_ocean(w.ocean, target)
        self._assert_img_equal("ocean_28070", target)

    def test_draw_precipitation(self):
        w = World.open_protobuf("%s/seed_28070.world" % self.tests_data_dir)
        target = PixelCollector(w.width, w.height)
        draw_precipitation(w, target)
        self._assert_img_equal("precipitation_28070", target)

    def test_draw_world(self):
        w = World.open_protobuf("%s/seed_28070.world" % self.tests_data_dir)
        target = PixelCollector(w.width, w.height)
        draw_world(w, target)
        self._assert_img_equal("world_28070", target)

    def test_draw_temperature_levels(self):
        w = World.open_protobuf("%s/seed_28070.world" % self.tests_data_dir)
        target = PixelCollector(w.width, w.height)
        draw_temperature_levels(w, target)
        self._assert_img_equal("temperature_28070", target)

    def test_draw_biome(self):
        w = World.open_protobuf("%s/seed_28070.world" % self.tests_data_dir)
        target = PixelCollector(w.width, w.height)
        draw_biome(w, target)
        self._assert_img_equal("biome_28070", target)

if __name__ == '__main__':
    unittest.main()
