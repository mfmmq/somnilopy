import logging
import mutagen
from flask import Response, jsonify, request, send_file, abort, Flask
from flask_restplus import Api, Resource, fields
from somnilopy.recordings_interface import RecordingsInterface
from somnilopy.api.restplus import api

file_handler = RecordingsInterface()
files_ns = api.namespace('files', description='Operations related to sleeptalking audio files')


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
        logging.info(f"Got file dates: {[date_group['date'] for date_group in files_by_date]}")
        return jsonify(files_by_date)


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
        return None


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
        # Make sure we have that file, else send a 404
        text, status = file_handler.apply_label(label, name, new_label)
        return Response(text, mimetype='text/html', status=status)

file_comment_model = files_ns.model("file_comment", {"comment": fields.String(description="New file comment", required=True)})

@files_ns.route('/<label>/<name>/comment')
class FilesItemComment(Resource):
    def get(self, label, name):
        '''
        Get the current comment of a file
        :param label:
        :param name:
        :return comment string stored in the file metadata:
        '''
        return file_handler.get_comment(label, name)

    @files_ns.expect(file_comment_model)
    def put(self, label, name):
        '''
        Update the comment of a file
        :param label:
        :param name:
        :return:
        '''
        try:
            file_handler.update_comment_from_label(label, name, request.json['comment'])
        except mutagen.MutagenError:
            return Response('No such file or directory', status=404)
        return Response('Successfully added comment', mimetype='text/html', status=200)


@files_ns.route('/<label>/<name>/download')
class FilesDownloadItem(Resource):
    def get(self, label, name):
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

