import logging
import os
import contextlib
import wave
from datetime import datetime
from flask import Flask, jsonify, Response, send_file
from flask_cors import CORS


def run_backend(autosave_dir, start_time, stop_time):
    app = Flask(__name__)
    CORS(app)
    prefix_dir = 'recordings'
    is_sleeptalking_dir = os.path.join('recordings', 'is-sleeptalking')
    not_sleeptalking_dir = os.path.join('recordings', 'not-sleeptalking')

    @app.route('/recording', methods=['GET'])
    def is_recording():
        if start_time < datetime.now().time < stop_time:
            return Response()
        else:
            return None

    @app.route('/files', methods=['GET'])
    def file_name():
        all_file_paths = [os.path.join(autosave_dir, file_name) for file_name in os.listdir(autosave_dir)]
        all_file_paths.extend([os.path.join(is_sleeptalking_dir, file_name) for file_name in os.listdir(is_sleeptalking_dir)])
        all_file_paths.extend([os.path.join(not_sleeptalking_dir, file_name) for file_name in os.listdir(not_sleeptalking_dir)])
        all_file_paths.sort(key=lambda x: os.path.getmtime(x))

        file_info = []
        for file_path in all_file_paths:
            try:
                date, time = file_path.split("_")[1:3]
                time = time.replace(".wav", "")
                time = time.replace("-", ":")[0:5]
                label, name = os.path.split(file_path)
                label = os.path.split(label)[1]
                with contextlib.closing(wave.open(file_path, 'r')) as f:
                    frames = f.getnframes()
                    rate = f.getframerate()
                    length = round(frames / float(rate), 2)
                file_info.append({"date": date, "time": time, "length": length, "name": name, "label": label})
            except ValueError:
                continue
        # Create a list of info grouped by date ie file: [..] date: 04-09
        files_by_date = []
        for file in file_info:
            if file['date'] not in [date_group['date'] for date_group in files_by_date]:
                files_by_date.append({'date': file['date'], 'files': []})
            for date_group in files_by_date:
                if file['date'] == date_group['date']:
                    date_group['files'].append(file)
        logging.debug(f"Got file dates: {[date_group['date'] for date_group in files_by_date]}")
        files_by_date.reverse()
        return jsonify(files_by_date)


    @app.route('/delete/<label>/<name>', methods=['DELETE'])
    def delete(label, name):
        # Make sure we have that file, else send a 404
        try:
            # Move to a not-sleeptalking folder
            current_path = os.path.join(prefix_dir, label, name)
            new_path = os.path.join(prefix_dir, 'delete', name)
            logging.info(f"Moving {current_path} to {new_path}")
            os.rename(current_path, new_path)
            return Response("Successfully deleted file", mimetype='text/html', status=200)
        except FileNotFoundError:
            # Send a 404 reponse back
            return Response("File not found", mimetype='text/html', status=404)

    @app.route('/download/<label>/<name>', methods=['GET'])
    def download(label, name):
        path = os.path.join('..', prefix_dir, label, name)
        return send_file(
            path,
            mimetype="audio/wav",
            as_attachment=True,
            attachment_filename=name)

    @app.route('/label/<new_label>/<old_label>/<name>', methods=['GET'])
    def move_folder(old_label, new_label, name):
        # Make sure we have that file, else send a 404
        try:
            old_label = os.path.join(prefix_dir, old_label)
            new_label = os.path.join(prefix_dir, new_label)
            # Move to label named folder
            current_path = os.path.join(old_label, name)
            new_path = os.path.join(new_label, name)
            os.rename(current_path, new_path)
            logging.info(current_path)
            logging.info(new_path)
            return Response("Successfully moved file", mimetype='text/html', status=200)
        except FileNotFoundError:
            # Send a 404 reponse back
            return Response("File not found", mimetype='text/html', status=404)

    app.run()
