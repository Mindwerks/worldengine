



def save_world(things_to_save,output_dir):
    """ takes a list of tuples, the tuple is "Object" "format"""
    
    for t in things_to_save:
        
        save_format=t[1]
        world=t[0]
        world_name=world.name
        world_format=save_format
        
        filename = "%s/%s.world" % (output_dir, world_name)
        if world_format == 'protobuf':
            save_world_to_protobuf(world,filename)
        elif world_format == "json":
            raise NotImplemented
            save_world_to_json(world,filename)
        elif world_format == 'hdf5':
            save_world_to_hdf5(world, filename)
        else:
            print("Unknown format '%s', not saving " % world_format)
        #print("* world data saved in '%s'" % filename)
        #sys.stdout.flush()

def save_world_to_protobuf(w,filename):
    with open(filename, "wb") as f:
        f.write(w.protobuf_serialize())

def save_world_to_hdf5(world,filename):
    a=1
    
def save_world_to_json(world,filename):
    a=1
