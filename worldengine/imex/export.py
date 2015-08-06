try:
    from osgeo import gdal
except ImportError:
    import gdal

import tempfile
import numpy
import os
import sys


def export(world, export_type, export_bpp, export_scale):
    inter_driver = gdal.GetDriverByName("GTiff")
    _, inter_file = tempfile.mkstemp()
    final_driver = gdal.GetDriverByName(export_type)
    if final_driver is None:
        print("%s driver not registered." % export_type)
        sys.exit(1)

    # massage data to scale between the absolute min and max of Uint16
    elevation = numpy.array(world.elevation['data'])
    if elevation.min() < 0.0:
        elevation += abs(elevation.min())
    elevation *= (2**export_bpp/elevation.max())

    if export_bpp == 8:
        elevation.astype(numpy.uint8)
        gdal_type = gdal.GDT_Byte
    elif export_bpp == 16:
        elevation.astype(numpy.uint16)
        gdal_type = gdal.GDT_UInt16
    elif export_bpp == 32:
        elevation.astype(numpy.uint32)
        gdal_type = gdal.GDT_UInt32

    # take elevation data and push it into an intermediate GTiff format
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
