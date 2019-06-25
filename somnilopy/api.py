import logging
from datetime import datetime
from flask import Flask, jsonify, Response, send_file, abort
from flask_cors import CORS
from flask_restful import Resource

class BackendApi:
    def __init__(self):
        self.hello = 0
        ns = api.namespace('blog/categories', description='Operations related to blog categories')

        class FilesCollection(Resource)

        @api.response(404, 'File not found.')
        class FilesItem(Resource)

def run_backend(start_time, stop_time, file_handler):
    '''
    Set up and run the back-end api for the frond-end that serves webpages and static files
    :param start_time:
    :param stop_time:
    :return:
    '''
    app = Flask(__name__)
    CORS(app)

    @app.route('/recording', methods=['GET'])
    def is_recording():
        if start_time < datetime.now().time < stop_time:
            return Response()
        else:
            return None

    @app.route('/files', methods=['GET'])
    def get_files_info():
        file_paths = file_handler.get_all_sorted_file_paths()
        file_info = []
        for file_path in file_paths:
            file_info.extend(file_handler.get_file_info_by_path(file_path))
        # Create a list of info grouped by date ie file: [..] date: 04-09

        files_by_date = []
        for file in file_info:
            if file['date'] not in [date_group['date'] for date_group in files_by_date]:
                files_by_date.append({'date': file['date'], 'files': []})
            for date_group in files_by_date:
                if file['date'] == date_group['date']:
                    date_group['files'].append(file)
        logging.info(f"Got file dates: {[date_group['date'] for date_group in files_by_date]}")
        return jsonify(files_by_date)

    @app.route('/files/<label>/<name>', methods=['DELETE'])
    def delete(label, name):
        # Make sure we have that file, else send a 404
        text, status = file_handler.delete(label, name)
        return Response(text, mimetype='text/html', status=status)

    @app.route('/files/<label>/<name>', methods=['GET'])
    def download(label, name):
        '''
        Endpoint to download any sleeptalking file. Use the label to get the folder its located in
        :param label:
        :param name:
        :return:
        '''
        path = file_handler.get_file_path_from_label(label, name)
        try:
            return send_file(
                path,
                mimetype="audio/flac",
                as_attachment=True,
                attachment_filename=name)
        except:
            abort(500, 'Error getting file')

    @app.route('/files/label/<old_label>/<name>/<new_label>', methods=['GET'])
    def move_folder(old_label, new_label, name):
        '''
        Move a file from one folder to another. This acts as a pseudo persistent label without having to
        modify comments or metadata. Having all the 'sleeptalking' and 'not sleeptalking' files in their
        respective folders also makes it easier to train models
        :param old_label:
        :param new_label:
        :param name:
        :return:
        '''
        # Make sure we have that file, else send a 404
        text, status = file_handler.apply_label(new_label, old_label, name)
        return Response(text, mimetype='text/html', status=status)

    @app.route('/files/comment/<label>/<name>', methods=['PUT'])
    def update_comment(label, name):
        if request.headers['Content-Type'] == 'text/plain':
            file_handler.update_comment(label, name, request.data)
        else:
            return "415 Unsupported Media Type"
        return Response('Successfully added comment', mimetype='text/html', status=200)

    logging.info('Starting up api')
    app.run()
