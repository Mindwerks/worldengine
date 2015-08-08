try:
    from osgeo import gdal
except ImportError:
    import gdal

import tempfile
import numpy
import os
import sys


def export(world, export_type, export_bpp, export_signed):
    final_driver = gdal.GetDriverByName(export_type)
    if final_driver is None:
        print("%s driver not registered." % export_type)
        sys.exit(1)

    if export_bpp == 8 and export_signed:
        numpy_type = numpy.int8
        gdal_type = gdal.GDT_Byte
    elif export_bpp == 8 and not export_signed:
        numpy_type = numpy.uint8
        gdal_type = gdal.GDT_Byte
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
    elevation = numpy.array(world.elevation['data'])

    if not export_signed and elevation.min() < 0.0:
        elevation += abs(elevation.min())+1

    elevation *= ((2**export_bpp)/elevation.max())

    elevation = elevation.astype(numpy_type)

    # take elevation data and push it into an intermediate GTiff format
    inter_driver = gdal.GetDriverByName("GTiff")
    _, inter_file = tempfile.mkstemp()
    initial_ds = inter_driver.Create(inter_file, world.height, world.width, 1, gdal_type)
    band = initial_ds.GetRasterBand(1)
    band.WriteArray(elevation)
    band = None  # dereference band
    initial_ds = None  # save/flush and close

    # take the intermediate GTiff format and convert to final format
    initial_ds = gdal.Open(inter_file)
    final_driver.CreateCopy('seed_output-%d.%s' % (export_bpp, export_type), initial_ds,
                            # options=["MINUSERPIXELVALUE=%f" % elevation.min(),
                            #          "MAXUSERPIXELVALUE=%f" % elevation.max()]
                            )

    os.remove(inter_file)
