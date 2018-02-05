
import worldengine
#import worldengine
import numpy


def main(args,arg_dict):

    #these are all default arguments.
    #they are just explicit right now.
    generation_operation=arg_dict["generation_operation"]
    operation=arg_dict["operation"]
    
    
    #if "seed" in arg_dict:
    
    
    world_format=arg_dict["world_format"]
    
    
    if "output_dir" not in arg_dict:
        raise ValueError
        
    #ha the actual operation. Neat.
    if operation == 'world':
        print('')  # empty line
        print('starting (it could take a few minutes) ...')
        
        #this needs some clean up, but later we can use kwargs
        world = plates.world_gen(seed=arg_dict["seed"],
                    world_name=arg_dict["world_name"]
                    arg_dict["width"],
                    arg_dict["height"],
                    temps=arg_dict["temps"],
                    humids=arg_dict["humids"],
                    arg_dict["number_of_plates"], 
                    arg_dict["ocean_level"],
                    step=arg_dict["step"])
                    
    if operation == 'plates':
        print('')  # empty line
        print('starting (it could take a few minutes) ...')

        generate_plates(seed, world_name, args.output_dir, args.width,
                        args.height, num_plates=args.number_of_plates)

    if operation == 'ancient_map':
        print('')  # empty line
        print('starting (it could take a few minutes) ...')
        # First, some error checking
        if args.sea_color == "blue":
            sea_color = (142, 162, 179, 255)
        elif args.sea_color == "brown":
            sea_color = (212, 198, 169, 255)
        else:
            usage("Unknown sea color: " + args.sea_color +
                  " Select from [" + SEA_COLORS + "]")
        if not args.world_file:
            usage(
                "For generating an ancient map is necessary to specify the " +
                "world to be used (-w option)")
        world = load_world(args.world_file)

        print_verbose(" * world loaded")

        if not args.generated_file:
            args.generated_file = "ancient_map_%s.png" % world.name
        operation_ancient_map(world, args.generated_file,
                              args.resize_factor, sea_color,
                              args.draw_biome, args.draw_rivers,
                              args.draw_mountains, args.draw_outer_border)
                              
    elif operation == 'info':
        world = load_world(args.FILE)
        print_world_info(world)
        
    elif operation == 'export':
        world = load_world(args.FILE)
        print_world_info(world)
        export(world, args.export_format, args.export_datatype, args.export_dimensions,
               args.export_normalize, args.export_subset,
               path='%s/%s_elevation' % (args.output_dir, world.name))
        
        
        
    save_data=True
    if save_data and operation in ["world"]:
        w=world
        save.save_world([[world,'protobuf']],arg_dict["output_dir"])

    draw=True
    if draw and operation in ["world","plates"]:
        
        output_dir=arg_dict["output_dir"]
        world_name=arg_dict["world_name"]
        
        black_and_white=False
        
        from draw import draw_ancientmap_on_file, draw_biome_on_file, draw_ocean_on_file, \
            draw_precipitation_on_file, draw_grayscale_heightmap_on_file, draw_simple_elevation_on_file, \
            draw_temperature_levels_on_file, draw_riversmap_on_file, draw_scatter_plot_on_file, \
            draw_satellite_on_file, draw_icecaps_on_file
        
        
        
        if operation=="plates":
            # Generate images
            filename = '%s/plates_%s.png' % (output_dir, world_name)
            draw_simple_elevation_on_file(world, filename, None)
            print("+ plates image generated in '%s'" % filename)
            filename = '%s/centered_plates_%s.png' % (output_dir, world_name)
            draw_simple_elevation_on_file(world, filename, None)
            print("+ centered plates image generated in '%s'" % filename)

        if operation=="world":
        # Generate images
            filename = '%s/%s_ocean.png' % (output_dir, world_name)
            draw_ocean_on_file(w.layers['ocean'].data, filename)
            print("* ocean image generated in '%s'" % filename)

            if step.include_precipitations:
                filename = '%s/%s_precipitation.png' % (output_dir, world_name)
                draw_precipitation_on_file(w, filename, black_and_white)
                print("* precipitation image generated in '%s'" % filename)
                filename = '%s/%s_temperature.png' % (output_dir, world_name)
                draw_temperature_levels_on_file(w, filename, black_and_white)
                print("* temperature image generated in '%s'" % filename)

            if step.include_biome:
                filename = '%s/%s_biome.png' % (output_dir, world_name)
                draw_biome_on_file(w, filename)
                print("* biome image generated in '%s'" % filename)

            
            filename = '%s/%s_elevation.png' % (output_dir, world_name)
            sea_level = w.sea_level()
            draw_simple_elevation_on_file(w, filename, sea_level=sea_level)
            print("* elevation image generated in '%s'" % filename)
        
            if args.grayscale_heightmap:
                #generate_grayscale_heightmap(world,
                #                             '%s/%s_grayscale.png' % (args.output_dir, world_name))
            
            #def generate_grayscale_heightmap(world, filename):
                draw_grayscale_heightmap_on_file(world, filename)
                print("+ grayscale heightmap generated in '%s'" % filename)
            
            if args.rivers_map:
                                
                #def generate_rivers_map(world, filename):
                draw_riversmap_on_file(world, filename)
                #print("+ rivers map generated in '%s'" % filename)

             #   generate_rivers_map(world,
             #                       '%s/%s_rivers.png' % (args.output_dir, world_name))
            if args.scatter_plot:
                
                            
            #def draw_scatter_plot(world, filename):
                draw_scatter_plot_on_file(world, filename)
                #print("+ scatter plot generated in '%s'" % filename)

                
                #draw_scatter_plot(world,
                #                  '%s/%s_scatter.png' % (args.output_dir, world_name))
                
                
            if args.satelite_map:
                
                            
            #def draw_satellite_map(world, filename):
                draw_satellite_on_file(world, filename)
            #    print("+ satellite map generated in '%s'" % filename)

                
                #draw_satellite_map(world,
                #                   '%s/%s_satellite.png' % (args.output_dir, world_name))
            if args.icecaps_map:
                
                

                #def draw_icecaps_map(world, filename):
                draw_icecaps_on_file(world, filename)
                #    print("+ icecap map generated in '%s'" % filename)

                
                #draw_icecaps_map(world,
                #                 '%s/%s_icecaps.png' % (args.output_dir, world_name))

    
    else:
        raise Exception(
            'Unknown operation: valid operations are %s' % OPERATIONS)

def generate_plates(seed, world_name, output_dir, width, height,
                    num_plates=10):
    """
    Eventually this method should be invoked when generation is called at
    asked to stop at step "plates", it should not be a different operation
    :param seed:
    :param world_name:
    :param output_dir:
    :param width:
    :param height:
    :param num_plates:
    :return:
    """
    
    #are you sure, this is what should be happening?
    
    elevation, plates = worldengine.plates.generate_plates_simulation(seed, width, height,
                                                   num_plates=num_plates)

    world = worldengine.world.World(world_name, Size(width, height), seed,
                  GenerationParameters(num_plates, -1.0, "plates"))
    world.elevation = (numpy.array(elevation).reshape(height, width), None)
    world.plates = numpy.array(plates, dtype=numpy.uint16).reshape(height, width)

    
    worldengine.generation.center_land(world)
    
def operation_ancient_map(world, map_filename, resize_factor, sea_color,
                          draw_biome, draw_rivers, draw_mountains,
                          draw_outer_land_border):
    draw_ancientmap_on_file(world, map_filename, resize_factor, sea_color,
                            draw_biome, draw_rivers, draw_mountains,
                            draw_outer_land_border, get_verbose())
    print("+ ancient map generated in '%s'" % map_filename)




def load_world(world_filename):
    pb = __seems_protobuf_worldfile__(world_filename)
    if pb:
        try:
            return worldengine.world.World.open_protobuf(world_filename)
        except Exception:
            raise Exception("Unable to load the worldfile as protobuf file")
    else:
        raise Exception("The given worldfile does not seem to be a protobuf file")

def with_cli():
    
    from os import path, pardir
    import sys
    print(path.dirname(path.realpath(__file__)))
    print( pardir)
    sys.path.append(path.join(path.dirname(path.realpath(__file__)), pardir))
    import cli
    args,arg_dict=cli.main()
    main(args,arg_dict)

if __name__ == "__main__":
    with_cli()
