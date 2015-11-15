import unittest
import os
import numpy
from worldengine.draw import _biome_colors, draw_simple_elevation, elevation_color, \
    draw_elevation, draw_riversmap, draw_grayscale_heightmap, draw_ocean, draw_precipitation, \
    draw_world, draw_temperature_levels, draw_biome, draw_scatter_plot, draw_satellite
from worldengine.biome import Biome
from worldengine.world import World
from worldengine.image_io import PNGWriter, PNGReader


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
        blessed_img = PNGReader("%s/%s.png" % (self.tests_blessed_images_dir, blessed_image_name))

        # check shapes (i.e. (height, width, channels)-tuple)
        self.assertTrue(blessed_img.array.shape == drawn_image.array.shape,
                        "Blessed and drawn images differ in height, width " +
                        "and/or amount of channels. Blessed %s, drawn %s"
                        % (str(blessed_img.array.shape), str(drawn_image.array.shape)))

        # compare images; cmp_array will be an array of booleans in case of equal shapes (and a pure boolean otherwise)
        cmp_array = blessed_img.array != drawn_image.array

        # avoid calling assertTrue if shapes differed; results would be weird (and meaningless)
        if numpy.any(cmp_array):
            diff = numpy.transpose(numpy.nonzero(cmp_array))  # list of tuples of differing indices
            self.assertTrue(False,
                            "Pixels at %i, %i are different. Blessed %s, drawn %s"
                            % (diff[0][0], diff[0][1],
                            blessed_img.array[diff[0][0], diff[0][1]],
                            drawn_image.array[diff[0][0], diff[0][1]]))


class TestDraw(TestBase):

    def setUp(self):
        super(TestDraw, self).setUp()

    def test_biome_colors(self):
        self.assertEqual(Biome.all_names(), sorted(_biome_colors.keys()))

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
        target = PNGWriter.rgba_from_dimensions(w.width, w.height)
        draw_simple_elevation(w, w.sea_level(), target)
        self._assert_img_equal("simple_elevation_28070", target)

    def test_draw_elevation_shadow(self):
        w = World.open_protobuf("%s/seed_28070.world" % self.tests_data_dir)
        data = w.elevation['data']
        target = PNGWriter.rgba_from_dimensions(w.width, w.height)
        draw_elevation(w, True, target)
        self._assert_img_equal("elevation_28070_shadow", target)

    def test_draw_elevation_no_shadow(self):
        w = World.open_protobuf("%s/seed_28070.world" % self.tests_data_dir)
        data = w.elevation['data']
        target = PNGWriter.rgba_from_dimensions(w.width, w.height)
        draw_elevation(w, False, target)
        self._assert_img_equal("elevation_28070_no_shadow", target)

    def test_draw_river_map(self):
        w = World.open_protobuf("%s/seed_28070.world" % self.tests_data_dir)
        target = PNGWriter.rgba_from_dimensions(w.width, w.height)
        draw_riversmap(w, target)
        self._assert_img_equal("riversmap_28070", target)

    def test_draw_grayscale_heightmap(self):
        w = World.open_protobuf("%s/seed_28070.world" % self.tests_data_dir)
        target = PNGWriter.grayscale_from_array(w.elevation['data'], scale_to_range=True)
        #draw_grayscale_heightmap(w, target)
        self._assert_img_equal("grayscale_heightmap_28070", target)

    def test_draw_ocean(self):
        w = World.open_protobuf("%s/seed_28070.world" % self.tests_data_dir)
        target = PNGWriter.rgba_from_dimensions(w.width, w.height)
        draw_ocean(w.ocean, target)
        self._assert_img_equal("ocean_28070", target)

    def test_draw_precipitation(self):
        w = World.open_protobuf("%s/seed_28070.world" % self.tests_data_dir)
        target = PNGWriter.rgba_from_dimensions(w.width, w.height)
        draw_precipitation(w, target)
        self._assert_img_equal("precipitation_28070", target)

    def test_draw_world(self):
        w = World.open_protobuf("%s/seed_28070.world" % self.tests_data_dir)
        target = PNGWriter.rgba_from_dimensions(w.width, w.height)
        draw_world(w, target)
        self._assert_img_equal("world_28070", target)

    def test_draw_temperature_levels(self):
        w = World.open_protobuf("%s/seed_28070.world" % self.tests_data_dir)
        target = PNGWriter.rgba_from_dimensions(w.width, w.height)
        draw_temperature_levels(w, target)
        self._assert_img_equal("temperature_28070", target)

    def test_draw_biome(self):
        w = World.open_protobuf("%s/seed_28070.world" % self.tests_data_dir)
        target = PNGWriter.rgba_from_dimensions(w.width, w.height)
        draw_biome(w, target)
        self._assert_img_equal("biome_28070", target)

    def test_draw_scatter_plot(self):
        w = World.open_protobuf("%s/seed_28070.world" % self.tests_data_dir)
        target = PNGWriter.rgba_from_dimensions(512, 512)
        draw_scatter_plot(w, 512, target)
        self._assert_img_equal("scatter_28070", target)

    def test_draw_satellite(self):
        w = World.open_protobuf("%s/seed_28070.world" % self.tests_data_dir)
        target = PNGWriter.rgba_from_dimensions(w.width, w.height)
        draw_satellite(w, target)
        self._assert_img_equal("satellite_28070", target)

if __name__ == '__main__':
    unittest.main()
