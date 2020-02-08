import logging
import argparse
import os
import sys
import threading
from somnilopy.recorder import Recorder
from somnilopy.backend import Backend

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
    parser.add_argument("--prefix",
                        help="Prefix of audio file names. Defaults to snippet",
                        dest="file_name",
                        action="store",
                        default="snippet",
                        type=str
                        )
    parser.add_argument("--min-threshold",
                        help="Minimum threshold to consider a noise as sleeptalking. Defaults to 800",
                        dest="min_threshold",
                        action="store",
                        default=800,
                        type=int
                        )
    args = parser.parse_args()
    return args


def setup_logging():
    logging.basicConfig(format="%(asctime)s - %(levelname)s [%(filename)s] - %(message)s",
                        level=logging.DEBUG)
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.WARNING)


if __name__ == "__main__":

    args = setup_argparse()
    setup_logging()

    snippets_queue = []
    autosave_dir = os.path.join('recordings', 'autosave')
    recorder = Recorder(args.schedule, args.force, args.min_threshold)
    backend = Backend(recorder)
    try:
        backend.run()
    except KeyboardInterrupt:
        sys.exit()
