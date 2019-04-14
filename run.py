import logging
import argparse
import os
from somnilopy.somnilopy import Somnilopy
from OpenSSL import SSL
from datetime import time
import wave
import contextlib

def setup_argparse():
    parser = argparse.ArgumentParser(description="Record sleeptalking")
    parser.add_argument("--schedule",
                        help="Set the schedule for when to record. Defaults to (and of format) 00:00>06:30",
                        dest="schedule",
                        default="00:00>06:30",
                        type=str)
    parser.add_argument("--force-record",
                        help="Force record audio even if not within schedule",
                        dest="force",
                        action="store_true",
                        default=False
                        )
    parser.add_argument("--dir",
                        help="Directory to save audio files in. Defaults to autosave",
                        dest="dir",
                        action="store",
                        default="autosave",
                        type=str
                        )
    parser.add_argument("--prefix",
                        help="Prefix of audio file names. Defaults to snippet",
                        dest="file_name",
                        action="store",
                        default="snippet",
                        type=str
                        )
    parser.add_argument("--min-threshold",
                    help="Minimum threshold to consider a noise as sleeptalking. Defaults to 600",
                    dest="min_threshold",
                    action="store",
                    default=600,
                    type=int
                    )
    args = parser.parse_args()
    return args


def setup_logging():
    logging.basicConfig(format="%(asctime)s - %(levelname)s [%(filename)s] - %(message)s",
                        level=logging.DEBUG)


if __name__ == "__main__":

    args = setup_argparse()
    setup_logging()

    snippets_queue = []
    somnilopy = Somnilopy(args.schedule, args.force, args.dir, args.file_name, args.min_threshold)
    #somnilopy.run()
    from flask import Flask, render_template, request, jsonify, Response, send_file
    from flask_cors import CORS
    app = Flask(__name__)
    CORS(app)

    @app.route('/files', methods = ['GET'])
    def file_name():
        all_file_paths = [os.path.join(args.dir, file_name) for file_name in os.listdir(args.dir)]
        all_file_paths.extend([os.path.join('is-sleeptalking', file_name) for file_name in os.listdir('is-sleeptalking')])
        all_file_paths.extend([os.path.join('not-sleeptalking', file_name) for file_name in os.listdir('not-sleeptalking')])
        all_file_paths.sort(key=lambda x: os.path.getmtime(x))

        file_info = []
        for file_path in all_file_paths:
            try:
                date, time = file_path.split("_")[1:3]
                time = time.replace(".wav","")
                time = time.replace("-",":")[0:5]
                label, name = os.path.split(file_path)
                with contextlib.closing(wave.open(file_path, 'r')) as f:
                     frames = f.getnframes()
                     rate = f.getframerate()
                     length = round(frames / float(rate),2)
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

    @app.route('/delete/<label>/<name>', methods = ['DELETE'])
    def delete(label, name):
        # Make sure we have that file, else send a 404
        try:
            # Move to a not-sleeptalking folder
            current_path = os.path.join(label, name)
            new_path = os.path.join('delete', name)
            os.rename(current_path, new_path)
            return Response("Successfully deleted file", mimetype='text/html', status=200)

        except FileNotFoundError:
            # Send a 404 reponse back
            return Response("File not found", mimetype='text/html', status=404)

    @app.route('/download/<label>/<name>', methods=['GET'])
    def download(label, name):
        path = os.path.join(label, name)
        return send_file(
            path,
            mimetype="audio/wav",
            as_attachment=True,
            attachment_filename=name)

    @app.route('/not-sleeptalking/<name>', methods=['GET'])
    def not_sleeptalking(name):
        # Make sure we have that file, else send a 404
        try:
            # Move to a not-sleeptalking folder
            current_path = os.path.join(args.dir, name)
            new_path = os.path.join('not-sleeptalking', name)
            os.rename(current_path, new_path)
            return Response("Successfully moved file", mimetype='text/html', status=200)

        except FileNotFoundError:
            # Send a 404 reponse back
            return Response("File not found", mimetype='text/html', status=404)

    @app.route('/label/<new_label>/<old_label>/<name>', methods=['GET'])
    def move_folder(old_label, new_label, name):
        # Make sure we have that file, else send a 404
        try:
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
