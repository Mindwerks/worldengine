from worldgen.continents import *
	

for i in xrange(10):
	plates = generate_plates(i)
	e = generate_base_heightmap(i,plates)
	w = world_gen(e,i)
	draw_biome(w.biome,'biome_%i.png' % i)
