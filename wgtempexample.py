from worldgen.continents import *

for i in xrange(10):
	draw_temp(temperature(i),"temp_%i.png" % i)
	draw_precipitation(precipitation(i),"precipitation_%i.png" % i)
	#draw_ocean(fill_ocean(e,sl),'ocean3.png')