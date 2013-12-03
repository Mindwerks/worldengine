import sys
import random
import jsonpickle

from geo import world_gen, World
from draw import draw_elevation

def droplet(world,pos):
    x,y = pos
    min_elev = world.elevation['data'][y][x]
    dest = None
    for p in world.tiles_around((x,y)):
        px,py = p
        e = world.elevation['data'][py][px]
        if e<min_elev:
            dest = p
    if dest:
        if world.is_land(dest):
            destx,desty = dest
            world.elevation['data'][desty][destx]-=0.5
            droplet(world,dest)
    else:
        world.elevation['data'][py][px]+=0.5

def erode(world,n):
    for i in xrange(n):
        if (i%50000==0):
            save(world,i)
        x,y = world.random_land()
        if random.random()<world.precipitation['data'][y][x]:
            droplet(world,(x,y))            

def save(world,i):
    filename = 'world_%s_elevation_at_%i.png' % (world.name,i)
    draw_elevation(world,filename)
    print("+ elevation image generated in '%s'" % filename)


def main():
    if len(sys.argv)!=3:
        usage()
    world_name = sys.argv[1]    
    drops      = int(sys.argv[2])
    random.seed()
    seed = random.randint(0,65536)
    print('Using seed %i to add rivers & erosion to world "%s". Drops=%i' % (seed,world_name,drops)) 

    # Load data
    filename = "worlds/world_%s.json" % world_name
    world = World.from_json_file(filename)
    print("+ data loaded from '%s'" % filename)

    erode(world,drops)

    # Generate images
    #filename = 'world_%s_elevation.png' % world_name
    #draw_elevation(world,filename)
    #print("+ elevation image generated in '%s'" % filename)

    # Generate images
    #filename = 'world_%s_biome.png' % world_name
    #draw_biome(w.biome,filename)
    #print("+ biome image generated in '%s'" % filename)

def usage():
    print ' -------------------------------------------------------------------------'
    print ' Federico Tomassetti, 2013'
    print ' World water generator'
    print ' '
    print ' water generator <world_name> <drops>'
    print ' -------------------------------------------------------------------------'
    sys.exit(' ')

#-------------------------------
if __name__ == "__main__":
    main()