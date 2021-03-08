from osgeo import gdal


def cutter(file_path, envelop):
    """
    Вырезает массив из первого канала одноканального geotiff, по заданным координатам.
    Возвращает массив данных, координаты левого верхнего угла в градусах, разрешение по x и y"""
    ds = gdal.Open(file_path, gdal.GA_ReadOnly)
    gt = ds.GetGeoTransform()
    rb = ds.GetRasterBand(1)

    minX = envelop[0]  # minL
    maxX = envelop[1]  # maxL
    minY = envelop[2]  # minB
    maxY = envelop[3]  # maxB

    px = int((maxX - gt[0]) / gt[1])
    py = int((maxY - gt[3]) / gt[5])
    px2 = int((minX - gt[0]) / gt[1])
    py2 = int((minY - gt[3]) / gt[5])

    arr = rb.ReadAsArray(px2, py, px - px2, py2 - py)

    return arr, gt[0] + gt[1] * px2, gt[3] + gt[5] * py, gt[1], gt[5]


if __name__ == "__main__":
    print("Hello from tiff_cutter")
