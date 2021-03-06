from datetime import datetime
import time
import schedule
import logging
import sys
from threading import Event, Thread
from somnilopy.sleeptalk_processor import SleeptalkProcessor
from somnilopy.sleeptalk_poller import SleeptalkPoller
from somnilopy.handlers.file_handler import FileHandler


class Recorder:
    def __init__(self, input_schedule, force_recording):
        """
        Class for setting up and running the processor, poller, and api backend
        The poller listens for sleeptalking and the processor handles speech recognition
        This is set on a separate thread to avoid slowing down the poller
        :param input_schedule: formatted string that describes when we should be listenning to sleep talking
        :param force_recording: a boolean override for whether or not to listen for sleeptalking
        """
        self.force_recording = force_recording
        self.start_time, self.stop_time = input_schedule.split('>')
        self._set_up_components()

    def _set_up_components(self):
        """
        Set up objects, threads, and stop event required as well as pointer to where the snippets should be stored
        in memory before they are saved
        :return:
        """
        self.snippets_queue = []
        self.stop_event = Event()
        self.stop_event.set()
        self.exit_event = Event()
        self.file_handler = FileHandler()
        self.poller = SleeptalkPoller(stop_event=self.stop_event)
        self.processor = SleeptalkProcessor(self.file_handler, stop_event=self.stop_event)
        self.thread = None

    def run(self):
        if self.force_recording:
            logging.info(f"Parameter --force-record is set")
            try:
                self.start_listening()
                while not self.exit_event.is_set():
                    time.sleep(1)
            except KeyboardInterrupt:
                logging.info('Exit signal received')
                self.exit()
        else:
            self.schedule()

    @staticmethod
    def is_time_between(start_time, stop_time, check_time=None):
        # If check time is not given, default to current UTC time
        check_time = check_time or datetime.now().time()
        logging.debug(f'Scheduled between {start_time} and {stop_time}. '
                      f'Current time is {check_time.strftime("%H:%M")}')
        if start_time < stop_time:
            return stop_time >= check_time >= start_time
        else:  # crosses midnight
            return check_time >= start_time or check_time <= stop_time

    def schedule(self):
        # If the current time is in between start and stop time, this will not start otherwise
        start_time = datetime.strptime(self.start_time, '%H:%M').time()
        stop_time = datetime.strptime(self.stop_time, '%H:%M').time()
        if self.is_time_between(start_time, stop_time):
            logging.debug("Current time is within schedule, starting now")
            self.start_listening()
        schedule.every().day.at(self.start_time).do(self.start_listening)
        schedule.every().day.at(self.stop_time).do(self.stop_listening)
        try:
            while not self.exit_event.is_set():
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info('KeyboardInterrupt received')
            self.exit()

    def exit(self):
        self.exit_event.set()
        schedule.clear()
        self.stop_listening()

    def start_listening(self):
        """
        Checks if we're already listenning and if not, starts everything up
        We create a new thread since threads can't be rerun
        :return:
        """
        if not self.stop_event.is_set():
            logging.warning(f'Tried to start listenning, but somnilopy is already recording')
            return None
        else:
            self.stop_event.clear()
            logging.info("Starting Somnilopy")
            self.poller.current_consumer = self.processor.consume()
            self.thread = Thread(target=self.poller.poll)
            self.thread.start()
            return True

    def stop_listening(self):
        """
        If we want to stop listening, try to exit our poller and processor threads cleanly. We want to exit cleanly
        just in case we are in the middle of recording or processing
        :return:
        """
        try:
            self.stop_event.set()
            self.poller.stop()
            return True
        except:
            return False

    def update_threshold(self, new_threshold):
        """
        Change the minimum gain a sound needs to reach be recorded
        Otherise, the sound will be discarded as noise and not sleeptalking
        :return:
        """
        self.poller.update_threshold(new_threshold)
        return None

    def update_schedule(self, start_time, stop_time):
        """
        Set the schedule for when recording starts and stops
        Must be formatted as HH:MM
        :return:
        """

        self.start_time = start_time
        self.stop_time = stop_time
        self._refresh_schedule()
        return

    def _refresh_schedule(self):
        if time.strptime(self.start_time, '%H:%M') < time.localtime() < time.strptime(self.stop_time, '%H:%M'):
            logging.debug("Current time is within schedule, starting now")
            self.start_listening()
        schedule.clear()
        schedule.every().day.at(self.start_time).do(self.start_listening)
        schedule.every().day.at(self.stop_time).do(self.stop_listening)
        return
