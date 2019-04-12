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
    args = parser.parse_args()
    return args


def setup_logging():
    logging.basicConfig(format="%(asctime)s - %(levelname)s [%(filename)s] - %(message)s",
                        level=logging.DEBUG)


if __name__ == "__main__":

    args = setup_argparse()
    setup_logging()

    snippets_queue = []
    somnilopy = Somnilopy(args.schedule, args.force, args.dir, args.file_name)
    #somnilopy.run()
    from flask import Flask, render_template, request, jsonify, Response, send_file
    from flask_cors import CORS
    app = Flask(__name__)
    CORS(app)

    @app.route('/files', methods = ['GET'])
    def file_name():
        all_file_names = os.listdir(args.dir)
        all_file_names.sort(key=lambda x: os.path.getmtime("autosave/"+x))

        file_info = []
        for name in all_file_names:
            date, time = name.split("_")[1:3]
            time = time.replace(".wav","")
            time = time.replace("-",":")[0:5]
            path = os.path.join(args.dir, name)
            with contextlib.closing(wave.open(path, 'r')) as f:
                 frames = f.getnframes()
                 rate = f.getframerate()
                 length = round(frames / float(rate),2)
            file_info.append({"date": date, "time": time, "length": length, "name": name})
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

    @app.route('/delete/<name>', methods = ['DELETE'])
    def delete():
        all_file_names = os.listdir(args.dir)
        file_info = []
        for name in all_file_names:
            date, time = name.split("_")[1:3]
            time = time.replace(".wav","")
            time = time.replace("-",":")
            with contextlib.closing(wave.open(os.path.join(args.dir, name), 'r')) as f:
                 frames = f.getnframes()
                 rate = f.getframerate()
                 length = frames / float(rate)
            file_info.append({"date": date, "time": time, "length": length})
        logging.info(file_info)
        return jsonify(file_info)

    @app.route('/download/<name>', methods=['GET'])
    def download(name):
        path = f"autosave/{name}"
        logging.info(path)
        return send_file(
            path,
            mimetype="x-please-download-audio/wav",
            as_attachment=True,
            attachment_filename=name)

    @app.route('/not-sleeptalking/<name>', methods=['GET']):
    def not_sleeptalking(name):
        return None

    app.run()