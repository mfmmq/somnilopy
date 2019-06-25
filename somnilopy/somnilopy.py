import time
import schedule
import logging
import sys
from threading import Thread, Event
from somnilopy.sleeptalk_processor import SleeptalkProcessor
from somnilopy.sleeptalk_poller import SleeptalkPoller
from somnilopy.api import run_backend
from somnilopy.file_handler import FileHandler


class Somnilopy:
    def __init__(self, input_schedule, force_recording, min_is_sleeptalking_threshold):
        '''
        Class for setting up and running the processor, poller, and api backend
        The poller listens for sleeptalking and the processor handles speech recognition
        This is set on a separate thread to avoid slowing down the poller
        :param input_schedule: formatted string that describes when we should be listenning to sleep talking
        :param force_recording: a boolean override for whether or not to listen for sleeptalking
        :param min_is_sleeptalking_threshold: an integer value that sets how sensitive the poller is to recording noise
               lower is more sensitive, higher is less sensitive
        '''
        self._set_up_constants(force_recording, input_schedule)
        self._set_up_components(min_is_sleeptalking_threshold)

    def _set_up_constants(self, force_recording, input_schedule):
        self.force_recording = force_recording
        self.start_time, self.stop_time = input_schedule.split('>')

    def _set_up_components(self, min_is_sleeptalking_threshold):
        '''
        Set up objects, threads, and stop event required as well as pointer to where the snippets should be stored
        in memory before they are saved
        :param min_is_sleeptalking_threshold:
        :return:
        '''
        self.snippets_queue = []
        self.stop_event = Event()
        self.file_handler = FileHandler()
        self.sleeptalk_poller = SleeptalkPoller(min_is_sleeptalking_threshold=min_is_sleeptalking_threshold)
        self.sleeptalk_processor = SleeptalkProcessor(self.file_handler)

        self.t_poller = Thread(target=self.sleeptalk_poller.listen_for_snippets,
                               args=(self.snippets_queue, self.stop_event))
        self.t_processor = Thread(target=self.sleeptalk_processor.process_snippets,
                                  args=(self.snippets_queue, self.stop_event))
        self.t_api = Thread(target=run_backend, args=(self.start_time, self.stop_time, self.file_handler))
        self.t_api.daemon = True  # This is so the api process is killed when the main process is killed

    def run(self):
        '''
        Function that
        :return:
        '''

        # I think we can get away with threading flask even though it should be on the main thread --
        # This application is fairly light and it shouldn't serve many requests at all
        self.t_api.start()
        if self.force_recording:
            logging.info(f"Parameter --force-record is set")
            self.start_listening()
            try:
                while True:
                    time.sleep(10)
            except KeyboardInterrupt:
                self.exit()
        else:
            # If the current time is in between start and stop time, this will not start otherwise
            if time.strptime(self.start_time, '%H:%M') < time.localtime() < time.strptime(self.stop_time, '%H:%M'):
                logging.debug("Current time is within schedule, starting now")
                self.start_listening()
            schedule.every().day.at(self.start_time).do(self.start_listening)
            schedule.every().day.at(self.stop_time).do(self.stop_listening)
            try:
                while True:
                    schedule.run_pending()
                    time.sleep(10)
            except KeyboardInterrupt:
                self.exit()

    def exit(self):
        schedule.clear()
        self.stop_listening()
        # Just kill process, since we don't need to e.g. free up any resources wrt the api
        sys.exit(0)

    def start_listening(self):
        '''

        :return:
        '''
        self.stop_event.clear()
        self.t_poller.start()
        self.t_processor.start()
        logging.info("Started Somnilopy")

    def stop_listening(self):
        '''
        If we want to stop listening, try to exit our poller and processor threads cleanly. We want to exit cleanly
        just in case we are in the middle of recording or processing
        :return:
        '''
        self.stop_event.set()
        try:
            self.t_poller.join()
            self.t_processor.join()
        except Exception as e:
            logging.error(f"Tried to stop somnilopy, but hit exception {e}")
            return False

        logging.info("Stopped Somnilopy")
        sys.exit(0)
        return True

