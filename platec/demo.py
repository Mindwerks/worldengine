import platec

p = platec.create()

from PIL import Image

def draw_elevation(data,filename,shadow=True,width=512,height=512):
    img = Image.new('RGBA',(width,height))
    pixels = img.load()

    min_elev = None
    max_elev = None
    for y in xrange(height):
        for x in xrange(width):
            e = data[y*width+x]
            if min_elev==None or e<min_elev:
                min_elev=e
            if max_elev==None or e>max_elev:
                max_elev=e              
    elev_delta = max_elev-min_elev  

    for y in range(0,height):
        for x in range(0,width):
            e = data[y*width+x]
            c = 255-int(((e-min_elev)*255)/elev_delta)
            pixels[x,y] = (c,c,c,255)
    img.save(filename)  

hm = platec.get_heightmap(p)
draw_elevation(hm,'pippo.png')

for i in range(2000000):
    platec.step(p)

hm = platec.get_heightmap(p)
draw_elevation(hm,'pippo1.png')