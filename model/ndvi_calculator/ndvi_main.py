from osgeo import ogr
import os
from datetime import datetime

from .two_tiff_from_hgt_creator import two_tiff_from_hgt
from .tiff_cutter import cutter
from .wkt_polygonizer import rasterize
from .ndiv_array_creator import ndvi_from_3_array
from .tiff_from_array import create_4_chanel_tiff_from_ndvi_array
from .ndvi_statistics import get_statistics


def ndvi(hgt_path, polygon_wkt):
    """
        Вход: путь к hgt файлу (пока только MOD09A1!!!!) и полигон WKT в проекции WGS84.
        Возвращает путь к tif с ndvi, минимальное, максимальное, среднее и медианное значение ndvi"""
    red_file, ni_file = two_tiff_from_hgt(hgt_path)

    geom_pol = ogr.CreateGeometryFromWkt(polygon_wkt)
    print(geom_pol.GetEnvelope())

    # Вырезаем красный канал по границам
    arr, x, y, dx, dy = cutter(red_file, geom_pol.GetEnvelope())

    # Вырезаем ближний инфракрасный канал по границам
    arr2, x2, y2, dx2, dy2 = cutter(ni_file, geom_pol.GetEnvelope())

    # По координатам полигона создаёмм массив для маскИрования
    arr3 = rasterize(polygon_wkt, len(arr[0]), len(arr))

    # Получаем массив со значениями ndvi в каждой ячейке
    arr4 = ndvi_from_3_array(arr, arr2, arr3)

    # Сохранение вырезанного куска в файл если вдруг понадобиться (так результат выглядит красиво)
    # ta.create_many_chanel_tiff_from_array([arr, arr2], x, y, dx, dy, "../HDF/f3.tiff", gdal.GDT_Float32)

    # Формирование имени выходного файла. Можно сделать на UUID. Но так пока удобнее.
    abs_path = os.path.abspath(hgt_path)
    dir = os.path.dirname(abs_path)
    time = datetime.today().strftime('%Y%m%d%H%M%S')
    out_path = dir + "/" + time + ".tif"
    tif_filename = '{}.tif'.format(time)

    # Запись в tif 4х цветной картинки с ndvi
    create_4_chanel_tiff_from_ndvi_array(arr4, x, y, dx, dy, out_path)


    # Получаем статистику по ndvi
    min, max, mean, median = get_statistics(arr4)

    return out_path, min, max, mean, median, tif_filename


