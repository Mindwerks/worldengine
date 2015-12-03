"""
To verify the behavior of drawing functions remain consistent we generate images, we verify them
manually and we recorded them as "blessed". Our tests verify we do not deviate from blessed images.

The images live in the worldengine-data repo: https://github.com/Mindwerks/worldengine-data

A script, generate_blessed_images, can be used to regenerate blessed images
"""

import os

from worldengine.model.world import *
from worldengine.draw import *
from worldengine.image_io import PNGWriter


def main(blessed_images_dir, tests_data_dir):
    w = World.open_protobuf("%s/seed_28070.world" % tests_data_dir)
    draw_simple_elevation_on_file(w, "%s/simple_elevation_28070.png"
                                  % blessed_images_dir, w.sea_level())
    draw_elevation_on_file(w, "%s/elevation_28070_shadow.png" % blessed_images_dir, shadow=True)
    draw_elevation_on_file(w, "%s/elevation_28070_no_shadow.png" % blessed_images_dir, shadow=False)
    draw_riversmap_on_file(w, "%s/riversmap_28070.png" % blessed_images_dir)
    draw_grayscale_heightmap_on_file(w, "%s/grayscale_heightmap_28070.png" % blessed_images_dir)
    draw_ocean_on_file(w.ocean, "%s/ocean_28070.png" % blessed_images_dir)
    draw_precipitation_on_file(w, "%s/precipitation_28070.png" % blessed_images_dir)
    draw_world_on_file(w, "%s/world_28070.png" % blessed_images_dir)
    draw_temperature_levels_on_file(w, "%s/temperature_28070.png" % blessed_images_dir)
    draw_biome_on_file(w, "%s/biome_28070.png" % blessed_images_dir)
    draw_scatter_plot_on_file(w, "%s/scatter_28070.png" % blessed_images_dir)
    draw_satellite_on_file(w, "%s/satellite_28070.png" % blessed_images_dir)
    draw_ancientmap_on_file(w, "%s/ancientmap_28070_factor3.png" % blessed_images_dir, resize_factor=3)

    img = PNGWriter.rgba_from_dimensions(w.width * 2, w.height * 2, "%s/rivers_28070_factor2.png" % blessed_images_dir)
    draw_rivers_on_image(w, img, factor=2)
    img.complete()

if __name__ == '__main__':
    blessed_images_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../worldengine-data/tests/images"))
    tests_data_dir = os.path.abspath(os.path.join(blessed_images_dir, '../data'))
    main(blessed_images_dir, tests_data_dir)
