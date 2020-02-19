import logging
import argparse
import os
import sys
from somnilopy.recorder import Recorder
from somnilopy.backend import Backend


def setup_argparse():
    parser = argparse.ArgumentParser(description="Record sleeptalking")
    parser.add_argument("--schedule",
                        help="Set the schedule for when to record. Defaults to (and of format) 00:00>06:30",
                        dest="schedule", default="00:40>06:30", type=str)
    parser.add_argument("--force-record", help="Force record audio even if not within schedule",
                        dest="force", action="store_true", default=False)
    parser.add_argument('--debug', help='Set debug logging to True', dest='debug', action='store_true', default=False)
    parser.add_argument('--server', help='Address and port to host at', dest='server', type=str, default=False)
    args = parser.parse_args()
    return args


def setup_logging(debug):
    if debug:
        logging.basicConfig(format="%(asctime)s - %(levelname)s [%(filename)s] - %(message)s",
                            level=logging.DEBUG)
    else:
        logging.basicConfig(format="%(asctime)s - %(levelname)s [%(filename)s] - %(message)s",
                            level=logging.INFO)
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.WARNING)


if __name__ == "__main__":

    args = setup_argparse()
    setup_logging(args.debug)

    snippets_queue = []
    recorder = Recorder(args.schedule, args.force)
    backend = Backend(recorder, args.server)
    try:
        backend.run()
    except KeyboardInterrupt:
        sys.exit()
