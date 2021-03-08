from osgeo import gdal, osr
import numpy as np


def create_many_chanel_tiff_from_array(arr, x, y, dx, dy, path, type):
    """
        Создаёт многоканальный tiff из массивов одинакового размера.
        Вход: arr - список массивов, x и y координаты левого верхнего угла в градусах,
        dx и dy разрешение по x и y, path - путь с именем файла, type - gdal.GDT_Byte или gdal.GDT_Float32
        Возвращает массив данных, координаты левого верхнего угла в градусах, разрешение по x и y"""
    wgs84 = osr.SpatialReference()
    wgs84.ImportFromEPSG(4326)
    driver = gdal.GetDriverByName("GTiff")

    outer_raster = driver.Create(path, len(arr[0][0]), len(arr[0]), len(arr), type)

    outer_raster.SetProjection(wgs84.ExportToWkt())
    outer_raster.SetGeoTransform([x, dx, 0, y, 0, dy])

    for i in range(len(arr)):
        outer_raster.GetRasterBand(i+1).WriteArray(arr[i])


def create_4_chanel_tiff_from_ndvi_array(arr, xin, yin, dx, dy, path):
    """
        Создаёт 4х канальный tiff из массива со значениями ndvi.
        Вход: arr - массив со значениями ndvi, xin и yin координаты левого верхнего угла в градусах,
        dx и dy разрешение по x и y, path - путь с именем файла"""

    r_pixels = np.zeros((len(arr), len(arr[0])), dtype=np.uint8)
    g_pixels = np.zeros((len(arr), len(arr[0])), dtype=np.uint8)
    b_pixels = np.zeros((len(arr), len(arr[0])), dtype=np.uint8)
    alpha_pixels = np.zeros((len(arr), len(arr[0])), dtype=np.uint8)

    #  Set the Pixel Data (Create some boxes)
    for x in range(0, len(arr)):
        for y in range(0, len(arr[x])):
            alpha_pixels[x, y] = 150
            if arr[x][y] == -100:
                alpha_pixels[x, y] = 0
                continue
            if arr[x][y] < 0:
                r_pixels[x, y] = 255
                continue
            if 0 <= arr[x][y] < 0.33:
                r_pixels[x, y] = 250
                g_pixels[x, y] = 90
                # b_pixels[x, y] = 20
                continue
            if 0.33 <= arr[x][y] < 0.66:
                r_pixels[x, y] = 255
                g_pixels[x, y] = 255
                continue
            else:
                g_pixels[x, y] = 255

    create_many_chanel_tiff_from_array([r_pixels, g_pixels, b_pixels, alpha_pixels], xin, yin, dx, dy, path, gdal.GDT_Byte)
