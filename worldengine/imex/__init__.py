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


'''
Whenever a GDAL short-format (http://www.gdal.org/formats_list.html) is given
and a unique mapping to a file suffix exists, it is looked up in gdal_mapper.

Trivial ones (i.e. a call to lower() does the job) are not handled:
   BAG, BMP, BT, ECW, ERS, FITS, GIF, GTA, PNG, RIK, VRT, XPM

All other formats (>100) currently end up with their respective GDAL short-format
converted to lower-case and might need to be renamed by the user.
'''
gdal_mapper = {  # TODO: Find a way to make GDAL provide this mapping.
    "aig"     : "adf",
    "bsb"     : "kap",
    "doq1"    : "doq",
    "doq2"    : "doq",
    "esat"    : "n1",
    "grib"    : "grb",
    "gtiff"   : "tif",
    "hfa"     : "img",
    "jdem"    : "mem",
    "jpeg"    : "jpg",
    "msgn"    : "nat",
    "terragen": "ter",
    "usgsdem" : "dem",
}


def export(world, export_filetype = 'GTiff', export_datatype = 'float32', path = 'seed_output'):
    try:
        gdal
    except NameError:
        print("Cannot export: please install pygdal.")
        sys.exit(1)

    final_driver = gdal.GetDriverByName(export_filetype)
    if final_driver is None:
        print("%s driver not registered." % export_filetype)
        sys.exit(1)

    # try to find the proper file-suffix
    export_filetype = export_filetype.lower()
    if export_filetype in gdal_mapper:
        export_filetype = gdal_mapper[export_filetype]

    # Note: GDAL will throw informative errors on its own whenever file type and data type cannot be matched.

    # translate export_datatype; http://www.gdal.org/gdal_8h.html#a22e22ce0a55036a96f652765793fb7a4
    export_datatype = export_datatype.lower()
    if export_datatype in ['gdt_byte', 'uint8', 'int8', 'byte', 'char']:  # GDAL does not support int8
        bpp, signed, normalize = (8, False, True)
        numpy_type = numpy.uint8
        gdal_type  = gdal.GDT_Byte
    elif export_datatype in ['gdt_uint16', 'uint16']:
        bpp, signed, normalize = (16, False, True)
        numpy_type = numpy.uint16
        gdal_type  = gdal.GDT_UInt16
    elif export_datatype in ['gdt_uint32', 'uint32']:
        bpp, signed, normalize = (32, False, True)
        numpy_type = numpy.uint32
        gdal_type  = gdal.GDT_UInt32
    elif export_datatype in ['gdt_int16', 'int16']:
        bpp, signed, normalize = (16, True, True)
        numpy_type = numpy.int16
        gdal_type  = gdal.GDT_Int16
    elif export_datatype in ['gdt_int32', 'int32', 'int']:  # fallback for 'int'
        bpp, signed, normalize = (32, True, True)
        numpy_type = numpy.int32
        gdal_type  = gdal.GDT_Int32
    elif export_datatype in ['gdt_float32', 'float32', 'float']:  # fallback for 'float'
        bpp, signed, normalize = (32, True, False)
        numpy_type = numpy.float32
        gdal_type  = gdal.GDT_Float32
    elif export_datatype in ['gdt_float64', 'float64']:
        bpp, signed, normalize = (64, True, False)
        numpy_type = numpy.float64
        gdal_type  = gdal.GDT_Float64
    else:
        raise TypeError("Type of data not recognized or not supported by GDAL: %s" % export_datatype)

    # massage data to scale between the absolute min and max
    elevation = numpy.copy(world.elevation['data'])

    # shift data according to minimum possible value
    if signed:
        elevation = elevation - world.sea_level()  # elevation 0.0 now refers to sea-level
    else:
        elevation -= elevation.min()  # lowest point at 0.0

    # rescale data (currently integer-types only)
    if normalize:
        # elevation maps usually have a range of 0 to 10, maybe 15 - rescaling for integers is essential
        if signed:
            elevation *= (2**(bpp - 1) - 1) / max(abs(elevation.min(), abs(elevation.max())))
        else:
            elevation *= (2**bpp - 1) / abs(elevation.max())

    # round data (integer-types only)
    if numpy_type != numpy.float32 and numpy_type != numpy.float64:
        elevation = elevation.round()

    # switch to final data type; no rounding performed
    elevation = elevation.astype(numpy_type)

    # take elevation data and push it into an intermediate GTiff format (some formats don't support being written by Create())
    inter_driver = gdal.GetDriverByName("GTiff")
    fh_inter_file, inter_file = tempfile.mkstemp()  # returns: (file-handle, absolute path)
    initial_ds = inter_driver.Create(inter_file, world.width, world.height, 1, gdal_type)
    band = initial_ds.GetRasterBand(1)
    
    band.WriteArray(elevation)
    band = None  # dereference band
    initial_ds = None  # save/flush and close

    # take the intermediate GTiff format and convert to final format
    initial_ds = gdal.Open(inter_file)
    final_driver.CreateCopy('%s-%d.%s' % (path, bpp, export_filetype), initial_ds)

    initial_ds = None
    os.close(fh_inter_file)
    os.remove(inter_file)
