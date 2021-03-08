import requests
import settings
import sys
from datetime import datetime
import numpy as np
from osgeo import ogr
from uuid import uuid1
from multiprocessing import Process
import os
import json
from .ndvi_calculator import ndvi_main
from typing import Optional, List
import time


def start_calc_ndvi(polygon: str, date: str):
    ogr_polygon = ogr.CreateGeometryFromWkt(polygon)
    linear_ring = ogr_polygon.GetGeometryRef(0)
    tmp = set()
    for i in range(0, linear_ring.GetPointCount()):
        point = linear_ring.GetPoint(i)
        hv = get_hv_by_coords(point[0], point[1])
        tmp.add(hv)
    if len(tmp) != 1:
        return None
    else:
        proc_uuid = str(uuid1())
        # lon = linear_ring.GetPoint(0)[0]
        # lat = linear_ring.GetPoint(0)[1]
        # formated_date = datetime.strptime(date, '%Y.%m.%d')
        try:
            proc_dir = '{}/{}'.format(settings.TMP_DATA_PATH, proc_uuid)
            os.mkdir(proc_dir)
            with open('{}/log.json'.format(proc_dir), 'w') as lof_f:
                log_message = {
                    'error': 0,
                    'total_progress': 0,
                    'cur_progress': 0,
                    'message': 'Загрузка исходных данных',
                }
                lof_f.write(json.dumps(log_message))
        except OSError as e:
            print(e)
        p = Process(target=start_calc_ndvi_proc,
                    args=(proc_uuid, polygon, date))
        p.start()
        # download_hdf(lon, lat, formated_date)
        return proc_uuid


def get_html(url: str) -> str:
    response = requests.get(url)
    return response.text


def get_dir_list() -> list:
    html = get_html(settings.COMMON_MODIS_DATA_URL)
    dirs = [line for line in html.split('\n') if '[DIR]' in line]
    folders = [folder.split('href="')[1].split('/">')[0] for folder in dirs]

    return folders


def get_hv_by_coords(lon: float, lat: float) -> str:
    settings_path = os.path.dirname(os.path.abspath(__file__))+"/../sn_bound_10deg.txt"
    data = np.genfromtxt(settings_path,
                         skip_header=7,
                         skip_footer=3)
    in_tile = False
    i = 0
    while not in_tile:
        in_tile = data[i, 4] <= lat <= data[i, 5] and data[i, 2] <= lon <= data[i, 3]
        i += 1

    vert = int(data[i - 1, 0])
    horiz = int(data[i - 1, 1])
    return 'h{:0>2d}v{:0>2d}'.format(horiz, vert)


def get_file_by_hv(date: datetime, hv: str) -> Optional[str]:
    date_str = date.strftime('%Y.%m.%d')
    html = get_html('{}/{}'.format(settings.COMMON_MODIS_DATA_URL, date_str))
    files = [file.split('href="')[1].split('">')[0] for file in html.split('\n') if hv in file]
    if len(files) == 0:
        return None
    hdf_file = [file for file in files if file.endswith('.hdf')][0]
    return hdf_file


def start_calc_ndvi_proc(proc_uuid: str, polygon: str, date: str):
    ogr_polygon = ogr.CreateGeometryFromWkt(polygon)
    linear_ring = ogr_polygon.GetGeometryRef(0)
    lon = linear_ring.GetPoint(0)[0]
    lat = linear_ring.GetPoint(0)[1]
    formatted_date = datetime.strptime(date, '%Y.%m.%d')
    log_file_path = '{}/{}/log.json'.format(settings.TMP_DATA_PATH, proc_uuid)

    hdf_file_path = download_hdf(lon, lat, formatted_date, proc_uuid)
    viktor_entry_point(polygon, hdf_file_path, log_file_path, proc_uuid)


def download_hdf(lon: float, lat: float, date: datetime, proc_uuid: str) -> Optional[str]:
    log_file_path = '{}/{}/log.json'.format(settings.TMP_DATA_PATH, proc_uuid)
    hv = get_hv_by_coords(lon, lat)
    date_str = date.strftime('%Y.%m.%d')
    file_name = get_file_by_hv(date, hv)
    if not file_name:
        update_log(log_file_path, error=1, message='Нет данных этого района для заданной даты', total_progress=100)
        raise Exception('Нет данных этого района для заданной даты')
    url = '{}/{}/{}'.format(settings.COMMON_MODIS_DATA_URL, date_str, file_name)
    # print(url)

    files = [
        {
            'name': file_name,
            'url': url
        },
        {
            'name': '{}.xml'.format(file_name),
            'url': '{}.xml'.format(url)
        }
    ]

    for file in files:
        file_name = file['name']
        url = file['url']
        hdf_file_path = '{}/{}'.format(settings.MODIS_DATA_PATH, file_name)
        if os.path.exists(hdf_file_path):
            continue
        with open(hdf_file_path, "wb") as f:
            print("Downloading {}".format(file_name))
            with requests.Session() as session:
                session.auth = (settings.NASA_USERNAME, settings.NASA_PASSWORD)
                r1 = session.request('get', url)
                response = session.get(r1.url, stream=True, auth=(settings.NASA_USERNAME, settings.NASA_PASSWORD))
                total_length = response.headers.get('content-length')

                if total_length is None:  # no content length header
                    f.write(response.content)
                else:
                    dl = 0
                    total_length = int(total_length)
                    for data in response.iter_content(chunk_size=1024 * 1024):
                        dl += len(data)
                        f.write(data)
                        done = int(100 * dl / total_length)
                        update_log(log_file_path, cur_progress=done, message='Загрузка файла: {}'.format(file_name))
                        sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (100 - done)))
                        sys.stdout.flush()
        update_log(log_file_path, total_progress=50)
    update_log(log_file_path, total_progress=90)
    return '{}/{}'.format(settings.MODIS_DATA_PATH, files[0]['name'])


def get_progress(proc_uuid):
    try:
        with open('{}/{}/log.json'.format(settings.TMP_DATA_PATH, proc_uuid)) as lof_f:
            log = lof_f.read()
            return json.loads(log)
    except:
        return None


def update_log(log_file_path: str,
               cur_progress: int = None,
               message: str = None,
               total_progress: int = None,
               error: int = None):
    with open(log_file_path, 'r') as log_f:
        cur_log = json.load(log_f)
    with open(log_file_path, 'w') as log_f:
        if cur_progress:
            cur_log['cur_progress'] = cur_progress
        if message:
            cur_log['message'] = message
        if total_progress:
            cur_log['total_progress'] = total_progress
        if error:
            cur_log['error'] = error
        log_f.write(json.dumps(cur_log))


def viktor_entry_point(polygon: str, hdf_file_path: str, log_file_path: str, proc_uuid: str):

    print(polygon, hdf_file_path)
    result_file, min, max, mean, median, tif_filename = ndvi_main.ndvi(hdf_file_path, polygon)
    print(result_file, min, max, mean, median)

    result_log_file_path = '{}/{}/result.json'.format(settings.TMP_DATA_PATH, proc_uuid)
    with open(result_log_file_path, 'w') as res_f:
        result_log_dict = {
            'tif_name': tif_filename,
            'min': float('{:.10f}'.format(min)),
            'max': float('{:.10f}'.format(max)),
            'mean': float('{:.10f}'.format(mean)),
            'median': float('{:.10f}'.format(median)),
        }
        res_f.write(json.dumps(result_log_dict))

    time.sleep(1)
    update_log(log_file_path, total_progress=100)


def get_result(proc_uuid: str) -> Optional[dict]:
    result_path = '{}/{}/result.json'.format(settings.TMP_DATA_PATH, proc_uuid)
    if os.path.exists(result_path):
        with open(result_path, 'r') as result_f:
            result_json = json.loads(result_f.read())
            return result_json
    return None
