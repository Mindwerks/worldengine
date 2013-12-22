import platec

platec.seed(3)
p = platec.create()

from PIL import Image

COLOR_STEP = 1.5

def my_color(c):
    if c < 0.5:
        return(0.0, 0.0, 0.25 + 1.5 * c)
    elif c < 1.0:
        return(0.0, 2 * (c - 0.5), 1.0)
    else:
      c -= 1.0;
      if c < 1.0 * COLOR_STEP:
        return(0.0, 0.5 +
            0.5 * c / COLOR_STEP, 0.0)
      elif (c < 1.5 * COLOR_STEP):
        return(2 * (c - 1.0 * COLOR_STEP) / COLOR_STEP, 1.0, 0.0)
      elif (c < 2.0 * COLOR_STEP):
        return(1.0, 1.0 - (c - 1.5 * COLOR_STEP) / COLOR_STEP, 0)
      elif (c < 3.0 * COLOR_STEP):
        return(1.0 - 0.5 * (c - 2.0 *
            COLOR_STEP) / COLOR_STEP,
            0.5 - 0.25 * (c - 2.0 *
            COLOR_STEP) / COLOR_STEP, 0)
      elif (c < 5.0 * COLOR_STEP):
        return(0.5 - 0.125 * (c - 3.0 *
            COLOR_STEP) / (2*COLOR_STEP),
            0.25 + 0.125 * (c - 3.0 *
            COLOR_STEP) / (2*COLOR_STEP),
            0.375 * (c - 3.0 *
            COLOR_STEP) / (2*COLOR_STEP))
      elif (c < 8.0 * COLOR_STEP):
        return(0.375 + 0.625 * (c - 5.0 *
            COLOR_STEP) / (3*COLOR_STEP),
            0.375 + 0.625 * (c - 5.0 *
            COLOR_STEP) / (3*COLOR_STEP),
            0.375 + 0.625 * (c - 5.0 *
            COLOR_STEP) / (3*COLOR_STEP))
      else:
        c -= 8.0 * COLOR_STEP
        while (c > 2.0 * COLOR_STEP):
            c -= 2.0 * COLOR_STEP
        return(1, 1 - c / 4.0, 1)

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
            #c = 255-int(((e-min_elev)*255)/elev_delta)
            #pixels[x,y] = (c,c,c,255)
            r,g,b = my_color(e)
            pixels[x,y]=(int(r*255),int(g*255),int(b*255),255)
    img.save(filename)  

hm = platec.get_heightmap(p)
draw_elevation(hm,'pippo.png')

for i in xrange(20):
    for j in xrange(100):
        platec.step(p)
    hm = platec.get_heightmap(p)
    draw_elevation(hm,'pippo%i.png' % i)