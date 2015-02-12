__author__ = 'Federico Tomassetti'

import unittest
import os
from PIL import Image
from lands.draw import *
from lands.draw import _biome_colors # need to be explicitly imported
from lands.world import *
from tests.draw_test import TestDraw, PixelCollector


class TestDrawingFunctions(TestDraw):

    def setUp(self):
        TestDraw.setUp(self)

    def test_draw_ancientmap(self):
        w = World.open_protobuf("%s/seed_28070.world" % self.tests_data_dir)
        target = PixelCollector(w.width, w.height)
        draw_biome(w, target)
        self._assert_img_equal("biome_28070", target)

if __name__ == '__main__':
    unittest.main()
