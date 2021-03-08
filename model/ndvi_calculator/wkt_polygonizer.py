from osgeo import gdal, ogr, osr


def rasterize(wkt_polygon, fxs, fys):
    sr = osr.SpatialReference()
    sr.ImportFromEPSG(4326)

    file_x_size = fxs
    file_y_size = fys

    # Create a memory raster to rasterize into.
    target_ds = gdal.GetDriverByName('MEM').Create('', file_x_size, file_y_size, 1, gdal.GDT_Byte)

    target_ds.SetProjection(sr.ExportToWkt())
    rast_ogr_ds = ogr.GetDriverByName('Memory').CreateDataSource( 'wrk' )
    rast_mem_lyr = rast_ogr_ds.CreateLayer( 'poly', srs=sr )

    feat = ogr.Feature( rast_mem_lyr.GetLayerDefn() )
    feat.SetGeometryDirectly( ogr.Geometry(wkt = wkt_polygon) )
    rast_mem_lyr.CreateFeature( feat )
    geom = feat.GetGeometryRef()

    x_rez = (geom.GetEnvelope()[1] - geom.GetEnvelope()[0]) / file_x_size
    y_rez = (geom.GetEnvelope()[3] - geom.GetEnvelope()[2]) / file_y_size

    target_ds.SetGeoTransform((geom.GetEnvelope()[0], x_rez, 0, geom.GetEnvelope()[3], 0, -1*y_rez))

    err = gdal.RasterizeLayer(target_ds, [1], rast_mem_lyr)

    return target_ds.GetRasterBand(1).ReadAsArray()

    # if err != 0:
    #     print(err)
    #     return 'fail'

    return 'success'
