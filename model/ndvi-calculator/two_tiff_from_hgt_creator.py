import os
import glob


def two_tiff_from_hgt(hgt_path):
    """
            Создаёт 2 tiff, вытаскивая красный и ближний инфракрасный канал из hdf.
            Файлы создаются рядом с hdf. Вытаскивают 1й и 5й каналы. Это соответствует MOD09A1.
            Вход: путь к файлу hdf"""

    abs_path = os.path.abspath(hgt_path)

    red_file = abs_path + '.red.tif'
    ni_file  = abs_path + '.ni.tif'

    # Вытаскивает красный канал из MOD09A1 с перепроецированием в WGS84 и сохранением в geoTiff в этом же каталоге
    red_command = "modis_convert.py -s \"(1)\" -e 4326 -o " + red_file  + " " + abs_path

    # Вытаскивает ближний инфракрасный канал из MOD09A1 с перепроецированием в WGS84 и
    # сохранением в geoTiff в этом же каталоге
    ni_command = "modis_convert.py -s \"(0 0 0 0 1)\" -e 4326 -o " + ni_file + " " + abs_path

    os.system(red_command)
    os.system(ni_command)

    red_file_full_path_list = glob.glob(red_file+'*')
    red_file_full_path = ''
    if len(red_file_full_path_list):
        red_file_full_path = red_file_full_path_list[0]

    ni_file_full_path_list = glob.glob(ni_file + '*')
    ni_file_full_path = ''
    if len(red_file_full_path_list):
        ni_file_full_path = ni_file_full_path_list[0]
    return red_file_full_path, ni_file_full_path
