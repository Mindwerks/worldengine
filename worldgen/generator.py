import sys
import random
import jsonpickle

from geo import world_gen
from draw import draw_biome
import geo
import draw

def generate_world(seed,world_name):
    w = world_gen(world_name,seed,verbose=True)

    # Save data
    filename = "world_%s.json" % world_name
    with open(filename, "w") as f:
        f.write(jsonpickle.encode(w))
    print("+ data saved in '%s'" % filename)

    # Generate images
    filename = 'world_%s_biome.png' % world_name
    draw_biome(w.biome,filename)
    print("+ biome image generated in '%s'" % filename)

def generate_plates(seed,world_name):
    plates = geo.generate_plates(seed)

    # Generate images
    filename = 'plates_%s.png' % world_name
    draw.draw_plates(plates,filename)
    print("+ plates image generated in '%s'" % filename)

def main():
    if len(sys.argv)<2:
        usage()
    world_name = sys.argv[1]    
    random.seed()
    if len(sys.argv)>=3:
        operation = sys.argv[2]
    else:
        operation = 'world'
    if len(sys.argv)==4:
        seed = int(sys.argv[3])
    else:
        seed = random.randint(0,65536)
    print('Using seed %i to generate %s "%s"' % (seed,operation,world_name)) 
    if operation=='world':
        generate_world(seed,world_name)
    elif operation=='plates':
        generate_plates(seed,world_name)
    elif:
        raise Exception('Unknown operation')

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