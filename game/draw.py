from PIL import Image

def civ_color(civ):
	h = hash(civ.name)
	r = (h % 256**1) / 256**0
	g = (h % 256**2) / 256**1
	b = (h % 256**3) / 256**2
	return (r,g,b,255)

def draw_civs(game,filename):
	w = game.world	
	img = Image.new('RGBA',(w.width,w.height))
	pixels = img.load()
	for y in range(0,w.height):
		for x in range(0,w.width):
			if w.is_land((x,y)):
				civ = game.civ_owning((x,y))
				if civ:
					pixels[x,y] = civ_color(civ)
				else:
					pixels[x,y] = (255,255,255,255)	
			else:
				pixels[x,y] = (0,0,255,255)
	img.save(filename)

