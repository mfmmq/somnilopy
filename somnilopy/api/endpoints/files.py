import logging
import mutagen
from flask import Response, jsonify, request, send_file, abort, Flask
from flask_restplus import Api, Resource, fields
from somnilopy.recordings_interface import RecordingsInterface
from somnilopy.api.restplus import api

file_handler = RecordingsInterface()
files_ns = api.namespace('files', description='Operations related to sleeptalking audio files')


def extract_time(json):
    try:
        # Also convert to int since update_time will be string.  When comparing
        # strings, "10" is smaller than "2".
        return json['date']
    except KeyError:
        return 0


@files_ns.route('/')
class FilesCollection(Resource):
    def get(self):
        '''
        Get information for all audio files
        :return: Returns
        '''
        file_paths = file_handler.get_all_sorted_file_paths()
        file_info = []
        for file_path in file_paths:
            file_info.extend(file_handler.get_file_info_by_path(file_path))
        logging.debug(file_info)
        # Create a list of info grouped by date ie file: [..] date: 04-09
        files_by_date = []
        for file in file_info:
            if file['date'] not in [date_group['date'] for date_group in files_by_date]:
                files_by_date.append({'date': file['date'], 'files': []})
            for date_group in files_by_date:
                if file['date'] == date_group['date']:
                    date_group['files'].append(file)
        files_by_date.sort(key=extract_time, reverse=True)
        logging.info(f"Got file dates: {[date_group['date'] for date_group in files_by_date]}")
        return jsonify(files_by_date)


file_info_model = files_ns.model("file_info", {"label": fields.String(description="New file label", required=False),
                                               "comment": fields.String(description="File metadata comment", required=False)})


@files_ns.route('/<label>/<name>')
@api.response(404, 'File not found.')
class FilesItem(Resource):
    def delete(self, label, name):
        '''
        Mark an audio file for deletion
        :param label:
        :param name:
        :return:
        '''
        # Make sure we have that file, else send a 404
        text, status = file_handler.delete(label, name)
        return Response(text, mimetype='text/html', status=status)

    def get(self, label, name):
        '''
        Get information on an audio file
        :param label:
        :param name:
        :return:
        '''
        info = file_handler.get_file_info_by_label(label, name)
        if info:
            return info
        else:
            return Response(status=404)

   # @files_ns.expect(file_info_model, validate=False)
    @api.response(403, 'Label not allowed')
    def put(self, label, name):
        '''
        Update the info of a file
        :param label:
        :param name:
        :return:
        '''
        content = request.json
        if 'label' in content:
            new_label = content['label']
            logging.info(f'Updating label of {name} with {new_label}')
            text, status = file_handler.apply_label(label, name, new_label)
        if 'comment' in content:
            new_comment = content['comment']
            text, status = file_handler.update_comment_from_label(label, name, new_comment)
        return Response(text, mimetype='text/html', status=status)


@files_ns.route('/<label>/<name>/label/<new_label>')
class Label(Resource):
    def put(self, label, name, new_label):
        '''
        Update the label of a file
        :param label:
        :param name:
        :param new_label:
        :return:
        '''
        try:
            # Make sure we have that file, else send a 404
            text, status = file_handler.apply_label(label, name, new_label)
            return Response(text, mimetype='text/html', status=status)
        except mutagen.MutagenError as e:
            logging.error(e)
            return Response('No such file or directory', status=404)


@files_ns.route('/<label>/<name>/download')
class FilesDownloadItem(Resource):
    def get(self, label, name):
        '''
        Endpoint to download any sleeptalking file. Use the label to get the folder its located in
        :param label:
        :param name:
        :return:
        '''
        path = '../' + file_handler.get_file_path_from_label(label, name)
        logging.info(path)
        try:
            return send_file(
                path,
                mimetype="audio/flac",
                as_attachment=True,
                attachment_filename=name)
        except:
            abort(500, 'Error getting file')

