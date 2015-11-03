from tmxlib.map import Map
from tmxlib.tileset import *
from tmxlib.tile import *
from PIL import Image


class WETileset(Tileset):

    def __init__(self, name, size):
        super(WETileset, self).__init__(name, size)
        self.ocean_image = Image.open("/home/federico/tmp/ocean.png")
        self.plain_image = Image.open("/home/federico/tmp/plain.png")
        self.spacing = (0, 0)
        self.margin = (0, 0)
        self.image = None

    def tile_image(self, number):
        if number == 0:
            return self.ocean_image
        elif number == 1:
            return self.plain_image
        else:
            raise Exception("Unknown number")

    def __len__(self):
        return 2


def export_to_tmx(world, tmx_filename):
    tile_size = (64, 64)
    map = Map((world.width, world.height), tile_size)
    map.add_layer('terrain')
    terrain = map.layers['terrain']
    terrain_tiles = WETileset('terrain_tiles', tile_size)

    ocean_tile = TilesetTile(terrain_tiles, 0)
    terrain_tiles.terrains.append_new('ocean', ocean_tile)
    plain_tile = TilesetTile(terrain_tiles, 1)
    terrain_tiles.terrains.append_new('plain', plain_tile)

    map.tilesets.insert(0, terrain_tiles)

    for y in range(world.height):
        for x in range(world.width):
            if world.is_land((x,y)):
                if world.is_mountain((x,y)):
                    terrain[x, y] = map.tilesets['terrain_tiles'][1]
                elif world.is_temperate_forest((x,y)):
                    terrain[x, y] = map.tilesets['terrain_tiles'][3]
                elif world.is_jungle((x,y)):
                    terrain[x, y] = map.tilesets['terrain_tiles'][4]
                else:
                    terrain[x, y] = map.tilesets['terrain_tiles'][0]
            else:
                terrain[x, y] = map.tilesets['terrain_tiles'][2]

    map.save(tmx_filename)