import worldengine

from worldengine.world import World
from worldengine import plates,save
from worldengine import cli

def main(args,arg_dict):
    #these are all default arguments.
    #they are just explicit right now.
    operation=arg_dict["operation"]
    
    if "save" in arg_dict:
        if arg_dict["save"]:
            if "output_dir" not in arg_dict:
                raise ValueError
    
    if operation == "plates": #no idea why you'd want this, but it's in the options.
        
        plates_kwargs=plates.filter_plates_args(arg_dict)
        e_as_array,p_as_array = plates.generate_plates_simulation(**plates_kwargs)
    
    if operation == 'world':
        print('')  # empty line
        print('starting (it could take a few minutes) ...')
        world_kwargs=filter_world_args(arg_dict)
        if "verbose" not in world_kwargs:
            world_kwargs["verbose"]=False

        world = World(**world_kwargs)
        
    
    elif operation == 'ancient_map':
        print('')  # empty line
        print('starting (it could take a few minutes) ...')
        # First, some error checking
        if args.sea_color == "blue":
            sea_color = (142, 162, 179, 255)
        elif args.sea_color == "brown":
            sea_color = (212, 198, 169, 255)
        else:
            raise ValueError
            
        
        world = load_world(args.world_file)

        #print_verbose(" * world loaded")

        if not args.generated_file:
            args.generated_file = "ancient_map_%s.png" % world.name
        operation_ancient_map(world, args.generated_file,
                              args.resize_factor, sea_color,
                              args.draw_biome, args.draw_rivers,
                              args.draw_mountains, args.draw_outer_border)
                              
    elif operation == 'info':
        world = load_world(args.FILE)
        cli.print_world_info(world)
        
    elif operation == 'export':
        #I can do this, but not here and not like this.
        raise NotImplemented
        
        #world = load_world(args.FILE)
        #print_world_info(world)
        #export to what? as what?
        #export(world, args.export_format, args.export_datatype, args.export_dimensions,
        #       args.export_normalize, args.export_subset,
        #       path='%s/%s_elevation' % (args.output_dir, world.name))
    
    else:
        raise Exception(
            'Unknown operation')

    save_data=arg_dict["save"]
    if save_data and operation in ["world"]:
        world
        save.save_world([[world,'protobuf']],arg_dict["output_dir"])

    draw=arg_dict["draw"]
    if draw and operation in ["world","plates"]:
        
        output_dir=arg_dict["output_dir"]
        world_name=arg_dict["world_name"]
        
        black_and_white=False
        
        from draw import draw_biome_on_file, draw_ocean_on_file, \
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
            draw_ocean_on_file(world.layers['ocean'].data, filename)
            print("* ocean image generated in '%s'" % filename)

            #if step.include_precipitations:
            filename = '%s/%s_precipitation.png' % (output_dir, world_name)
            draw_precipitation_on_file(world, filename, black_and_white)
            print("* precipitation image generated in '%s'" % filename)
            filename = '%s/%s_temperature.png' % (output_dir, world_name)
            draw_temperature_levels_on_file(world, filename, black_and_white)
            print("* temperature image generated in '%s'" % filename)

            filename = '%s/%s_biome.png' % (output_dir, world_name)
            draw_biome_on_file(world, filename)
            print("* biome image generated in '%s'" % filename)

            filename = '%s/%s_elevation.png' % (output_dir, world_name)
            sea_level = world.sea_level()
            draw_simple_elevation_on_file(world, filename, sea_level=sea_level)
            print("* elevation image generated in '%s'" % filename)
        
            if args.grayscale_heightmap:
                #generate_grayscale_heightmap(world,
                #                             '%s/%s_grayscale.png' % (args.output_dir, world_name))
                draw_grayscale_heightmap_on_file(world, filename)
                print("+ grayscale heightmap generated in '%s'" % filename)
            
            if args.rivers_map:
                draw_riversmap_on_file(world, filename)
                #print("+ rivers map generated in '%s'" % filename)

             #   generate_rivers_map(world,
             #                       '%s/%s_rivers.png' % (args.output_dir, world_name))
            if args.scatter_plot:
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

def filter_world_args(all_dict):
    l=["name","seed","width","height","temps","humids","number of plates","ocean_level","step","verbose"]
    
    world_kwargs={}
    
    for key in l:
        if key in all_dict:
            world_kwargs[key]=all_dict[key]
    print("wkwargs",world_kwargs)
    return world_kwargs

def operation_ancient_map(world, map_filename, resize_factor, sea_color,
                          draw_biome, draw_rivers, draw_mountains,
                          draw_outer_land_border,verbose=False):
                              
    from draw import draw_ancientmap_on_file
    draw_ancientmap_on_file(world, map_filename, resize_factor, sea_color,
                            draw_biome, draw_rivers, draw_mountains,
                            draw_outer_land_border, verbose)
    print("+ ancient map generated in '%s'" % map_filename)

def load_world(world_filename):
    pb = __seems_protobuf_worldfile__(world_filename)
    if pb:
        try:
            return World.open_protobuf(world_filename)
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
