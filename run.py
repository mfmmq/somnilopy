import logging
import argparse
import os
from somnilopy.somnilopy import Somnilopy

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
    from flask import Flask, render_template, request, jsonify, Response
    app = Flask(__name__)

    @app.route('/', methods = ['GET'])
    def home():
        all_file_names = os.listdir(args.dir)
        file_info = []
        for name in all_file_names:
            day, time = name.split("_")[1:3]
            with contextlib.closing(wave.open(audiofile, 'r')) as f:
                frames = f.getnframes()
                rate = f.getframerate()
                length = frames / float(rate)
                print(length)
                file_info.append({"day": day, "time": time, "length": length})

        return render_template("index.html", file_info=file_info)
    app.run()