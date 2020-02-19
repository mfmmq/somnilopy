import logging
from datetime import datetime
from flask import Response, jsonify, request, send_file, abort
from flask_restplus import Resource, fields
from somnilopy.handlers.file_handler import FileHandler
from somnilopy.api.restplus import api
from somnilopy import settings

file_handler = FileHandler()
files_ns = api.namespace('files', description='Operations related to sleeptalking audio files')

file_info_model = files_ns.model("info", {"label": fields.String(description="New file label", required=False),
                                          "comment": fields.String(description="New file comment", required=False)})


def extract_timestamp(filename):
    try:
        filename, _ = filename.split('.')
        return datetime.strptime(filename[-19:], settings.TIMESTAMP_FORMAT)
    except:
        return datetime.now()


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
    @api.response(200, 'Successfully got information for audio files')
    def get(self):
        """
        Get information for some audio files, based on pagination.
        Getting information for all audio files can be expensive, so allow returning only n at one time
        :param dates: Number of dates to get all file info for
        :param offset: Offset to start count from. This system is fairly rudimentary and doesn't use an id
        :param descending: Start from latest date if True
        :return:
        """
        args = request.args
        no_break = bool(args.get('no_break', False))
        descending = bool(args.get('descending', True))
        offset = int(args.get('offset', 0))
        files_by_date = file_handler.get_file_paths_by_date(no_break=no_break)
        dates = files_by_date.keys()
        count = int(args.get('count', len(dates)))
        dates = sorted(list(dates), reverse=descending)
        dates = dates[offset:count + offset]
        for date in dates:
            files_by_date[date] = [file_handler.get_file_info_by_path(path)[0] for path in files_by_date[date]]
        files_by_date = [{'date': date, 'files': files_by_date[date]} for date in dates]
        files_by_date.sort(key=extract_date, reverse=descending)
        logging.info(f'Got files for dates {[d["date"] for d in files_by_date]}')
        return jsonify(files_by_date)

    @staticmethod
    def _process_file_info(file_info):
        """
        Create a list of info grouped by date ie file: [..] date: 04-09
        This will make things easier to display on the frontend
        :param file_info:
        :return:
        """
        file_info.sort(key=lambda f: f['time'])
        files_by_date = []
        for file in file_info:
            if file['date'] not in [date_group['date'] for date_group in files_by_date]:
                files_by_date.append({'date': file['date'], 'files': []})
            for date_group in files_by_date:
                if file['date'] == date_group['date']:
                    date_group['files'].append(file)
        files_by_date.sort(key=extract_date, reverse=True)
        return files_by_date


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
        try:
            return send_file(
                path,
                mimetype="audio/flac",
                as_attachment=True,
                attachment_filename=name)
        except:
            abort(500, 'Error getting file')
