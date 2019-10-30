import logging
import mutagen
from flask import Response, jsonify, request, send_file, abort, Flask
from flask_restplus import Api, Resource, fields
from somnilopy.file_handler import FileHandler
from somnilopy.api.restplus import api


file_handler = FileHandler()
files_ns = api.namespace('files', description='Operations related to sleeptalking audio files')


def extract_time(json):
    try:
        # Also convert to int since update_time will be string.  When comparing
        # strings, "10" is smaller than "2".
        return json['time']
    except KeyError:
        return 0


def extract_date(json):
    try:
        # Also convert to int since update_time will be string.  When comparing
        # strings, "10" is smaller than "2".
        return json['date']
    except KeyError:
        return 0


@files_ns.route('/')
class FilesCollection(Resource):
    @api.response(200, 'Successfully got information for all audio files')
    def get(self):
        """
        Get information for all audio files
        :return: Returns
        """
        file_paths = file_handler.get_all_file_paths()
        file_info = []
        for file_path in file_paths:
            file_info.extend(file_handler.get_file_info_by_path(file_path))
        file_info.sort(key=lambda f: f['time'])
        logging.info(file_info)
        # Create a list of info gro
        # Create a list of info grouped by date ie file: [..] date: 04-09
        files_by_date = []
        for file in file_info:
            if file['date'] not in [date_group['date'] for date_group in files_by_date]:
                files_by_date.append({'date': file['date'], 'files': []})
            for date_group in files_by_date:
                if file['date'] == date_group['date']:
                    date_group['files'].append(file)
        files_by_date.sort(key=extract_date, reverse=True)

        return jsonify(files_by_date)


file_info_model = files_ns.model("info", {"label": fields.String(description="New file label", required=False),
                                          "comment": fields.String(description="New file comment", required=False)})


@files_ns.route('/<name>')
@api.response(404, 'File not found.')
class FilesItem(Resource):
    @api.response(200, 'Successfully marked file for deletion')
    def delete(self, name):
        """
        Mark an audio file for deletion
        :param label:
        :param name:
        :return:
        """
        # Make sure we have that file, else send a 404
        status = file_handler.delete(name)
        return Response('', mimetype='text/html', status=status)

    @api.response(200, 'Succesfully got file metadata')
    def get(self, name):
        """
        Get information on an audio file
        :param label:
        :param name:
        :return:
        """
        info = file_handler.get_file_info_by_name(name)
        if info:
            return info
        else:
            return Response(status=404)

    @files_ns.expect(file_info_model, validate=False)
    @api.response(200, 'Successfully updated file metadata')
    def put(self, name):
        """
        Update the info of a file
        :param label:
        :param name:
        :return:
        """
        content = request.json
        if 'label' in content:
            new_label = content['label']
            logging.info(f'Updating label of {name} with {new_label}')
            file_handler.apply_label(name, new_label)
        if 'comment' in content:
            new_comment = content['comment']
            logging.info(f'Updating comment of {name} with {new_comment}')
            file_handler.update_comment_from_name(name, new_comment)
        return Response('Successfully updated file metadata', status=200)


@files_ns.route('/<name>/download')
class FilesDownloadItem(Resource):
    @api.response(200, 'Successfully got file')
    def get(self, name):
        """
        Endpoint to download any sleeptalking file. Use the label to get the folder its located in
        :param label:
        :param name:
        :return:
        """
        path = '../' + file_handler.get_file_path_from_name(name)
        logging.info(path)
        try:
            return send_file(
                path,
                mimetype="audio/flac",
                as_attachment=True,
                attachment_filename=name)
        except:
            abort(500, 'Error getting file')
