from worldgen.continents import *

for i in xrange(10):
	plates = generate_plates(i)
	e = generate_base_heightmap(i,plates)
	#draw_elevation(e,'elev3.png')
	sl = find_elevation(e,0.3)
	ocean = fill_ocean(e,sl+1.5)
	hl = find_elevation(e,0.10)
	ml = find_elevation(e,0.03)
	draw_land(e,ocean,hl,ml,"land_%i.png" % i)
	print("Generated world %i" % i)
	#draw_ocean(fill_ocean(e,sl),'ocean3.png')