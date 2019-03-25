import logging
import argparse
from somnilopy.somnilopy import Somnilopy


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
    somnilopy.run()
