__author__ = 'Federico Tomassetti'

import unittest

from lands.drawing_functions import *
from lands.world import *
from tests.draw_test import TestBase, PixelCollector, TestDraw


class TestDrawingFunctions(TestBase):

    def setUp(self):
        super(TestDrawingFunctions, self).setUp()

    def test_draw_ancientmap_factor1(self):
        w_large = World.from_pickle_file("%s/seed_48956.world" % self.tests_data_dir)
        target = PixelCollector(w_large.width, w_large.height)
        draw_ancientmap(w_large, target, resize_factor=1)
        self._assert_img_equal("ancientmap_48956", target)

    def test_draw_ancientmap_factor3(self):
        w = World.open_protobuf("%s/seed_28070.world" % self.tests_data_dir)
        target = PixelCollector(w.width * 3, w.height * 3)
        draw_ancientmap(w, target, resize_factor=3)
        self._assert_img_equal("ancientmap_28070_factor3", target)

if __name__ == '__main__':
    unittest.main()
