from flask import Flask, jsonify, request
from flask_cors import CORS
import os

from model import modis_service
import settings

app = Flask(__name__)
CORS(app)


@app.before_first_request
def before_fr():
    try:
        os.mkdir(settings.TMP_DATA_PATH)
    except OSError as e:
        print(e)
    try:
        os.mkdir(settings.MODIS_DATA_PATH)
    except OSError as e:
        print(e)


@app.route('/get_folder_list')
def get_folder_list():
    folder_list = modis_service.get_dir_list()
    return jsonify(folder_list)


@app.route('/calc_ndvi', methods=['POST'])
def calc_ndvi():
    data = request.json
    proc_uuid = modis_service.start_calc_ndvi(data['polygon'], data['date'])
    if not proc_uuid:
        return jsonify({'error': 1,
                        'message': 'Границы поля выодят за пределы одного листа данных. '
                                   'Сожалеем, но этот функционал ещё не реализован.'})
    return jsonify(proc_uuid)


@app.route('/get_progress')
def get_progress():
    proc_uuid = request.args.get('proc_uuid')
    res = modis_service.get_progress(proc_uuid)
    if res:
        return jsonify(res)
    else:
        return jsonify('not ok')


if __name__ == '__main__':
    app.run()
