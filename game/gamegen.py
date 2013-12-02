import sys
import random
import jsonpickle

from geo import world_gen
from draw import draw_biome

def main():
    if len(sys.argv)<4:
        usage()
    world_name = sys.argv[1] 
    game_name  = sys.argv[2]
    turns      = int(sys.argv[3])  
    random.seed()
    seed = random.randint(0,65536)
    print('Using seed %i to generate game "%s"' % (seed,game_name)) 

    TO UPDATE
    w = world_gen(world_name,seed)

    # Save data
    filename = "world_%s.json" % world_name
    with open(filename, "w") as f:
        f.write(jsonpickle.encode(w))
    print("+ data saved in '%s'" % filename)

    # Generate images
    filename = 'world_%s_biome.png' % world_name
    draw_biome(w.biome,filename)
    print("+ biome image generated in '%s'" % filename)

def usage():
    print ' -------------------------------------------------------------------------'
    print ' Federico Tomassetti, 2013'
    print ' World generator'
    print ' '
    print ' generator <world_name>'
    print ' -------------------------------------------------------------------------'
    sys.exit(' ')

#-------------------------------
if __name__ == "__main__":
    main()