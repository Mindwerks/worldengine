import platec

from PIL import Image



platec.seed(3)
p = platec.create()

hm = platec.get_heightmap(p)
draw_elevation(hm,'pippo.png')

for i in xrange(20):
    for j in xrange(100):
        platec.step(p)
        r = platec.is_finished(p) 
        if r>0:
            break
    if r>0:
        break
    hm = platec.get_heightmap(p)
    draw_elevation(hm,'pippo%i.png' % i)

hm = platec.get_heightmap(p)
draw_elevation(hm,'pippo_final.png')