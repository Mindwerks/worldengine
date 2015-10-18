try:
    from osgeo import gdal
except ImportError:
    try:
        import gdal
    except ImportError:
        print("Unable to load GDAL support, no heightmap export possible.")

import tempfile
import numpy
import os
import sys


def export(world, export_filetype, export_bpp, export_signed, path = 'seed_output', export_raw = True):
    try:
        gdal
    except NameError:
        print("Cannot export: please install pygdal.")
        sys.exit(1)

    final_driver = gdal.GetDriverByName(export_filetype)
    if final_driver is None:
        print("%s driver not registered." % export_filetype)
        sys.exit(1)

    #check settings for some common filetypes
    if export_filetype.lower() == 'png':
        if export_signed != False or (export_bpp != 8 and export_bpp != 16):
            print("A grayscale PNG only supports unsigned 8 or 16 Bit integers.")
        export_raw = False
        export_signed = False
        if export_bpp <= 8:
            export_bpp = 8
        else:
            export_bpp = 16
    elif export_filetype.lower() == 'bmp':
        if export_signed != False or export_bpp != 8:
            print("GDAL only supports export to BMP as unsigned 8 Bit integers.")
        export_raw = False
        export_signed = False
        export_bpp = 8

    #process basic settings
    if export_raw:
        export_signed = True
        export_bpp = 32
        numpy_type = numpy.float32
        gdal_type = gdal.GDT_Float32
    elif export_bpp == 8 and export_signed:
        print("Export of signed 8BPP is not supported by GDAL. Switching to unsigned 8BPP.")
        export_signed = False
        numpy_type = numpy.uint8
        gdal_type = gdal.GDT_Byte#always unsigned!
    elif export_bpp == 8 and not export_signed:
        numpy_type = numpy.uint8
        gdal_type = gdal.GDT_Byte#always unsigned!
    elif export_bpp == 16 and export_signed:
        numpy_type = numpy.int16
        gdal_type = gdal.GDT_Int16
    elif export_bpp == 16 and not export_signed:
        numpy_type = numpy.uint16
        gdal_type = gdal.GDT_UInt16
    elif export_bpp == 32 and export_signed:
        numpy_type = numpy.int32
        gdal_type = gdal.GDT_Int32
    elif export_bpp == 32 and not export_signed:
        numpy_type = numpy.uint32
        gdal_type = gdal.GDT_UInt32
    else:
        print ("BPP %d is not valid, we only support 8, 16 and 32." % export_bpp)
        sys.exit(1)

    # massage data to scale between the absolute min and max
    elevation = numpy.copy(world.elevation['data'])

    if export_signed:
        elevation = elevation - world.sea_level()#elevation 0 now refers to sea-level
    else:
        elevation -= elevation.min()#place the lowest point of the world at 0.0

    if not export_raw:#make best possible use of the available range; only available for integer exports
        if export_signed:
            elevation *= (2**(export_bpp - 1) - 1) / max(abs(elevation.min(), abs(elevation.max())))
        else:
            elevation *= (2**export_bpp - 1) / abs(elevation.max())

    elevation = elevation.astype(numpy_type)#no rounding performed

    # take elevation data and push it into an intermediate GTiff format
    inter_driver = gdal.GetDriverByName("GTiff")
    _, inter_file = tempfile.mkstemp()#returns (file-handle, absolute path)
    initial_ds = inter_driver.Create(inter_file, world.width, world.height, 1, gdal_type)
    band = initial_ds.GetRasterBand(1)
    
    band.WriteArray(elevation)
    band = None  # dereference band
    initial_ds = None  # save/flush and close

    # take the intermediate GTiff format and convert to final format
    initial_ds = gdal.Open(inter_file)
    final_driver.CreateCopy('%s-%d.%s' % (path, export_bpp, export_filetype.lower()), initial_ds)#TODO: find a way to extract the proper file-suffix from the GDAL filetype

    os.remove(inter_file)
