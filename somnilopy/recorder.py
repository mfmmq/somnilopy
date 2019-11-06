from datetime import time, datetime
import time as time2
import schedule
import logging
import sys
import re
from threading import Thread, Event
from somnilopy.sleeptalk_processor import SleeptalkProcessor
from somnilopy.sleeptalk_poller import SleeptalkPoller
from somnilopy.file_handler import FileHandler

file_handler = FileHandler()


class Recorder:
    def __init__(self, input_schedule, force_recording, min_is_sleeptalking_threshold):
        """
        Class for setting up and running the processor, poller, and api backend
        The poller listens for sleeptalking and the processor handles speech recognition
        This is set on a separate thread to avoid slowing down the poller
        :param input_schedule: formatted string that describes when we should be listenning to sleep talking
        :param force_recording: a boolean override for whether or not to listen for sleeptalking
        :param min_is_sleeptalking_threshold: an integer value that sets how sensitive the poller is to recording noise
               lower is more sensitive, higher is less sensitive
        """
        self.force_recording = force_recording
        self.start_time, self.stop_time = input_schedule.split('>')
        self._set_up_components(min_is_sleeptalking_threshold)

    def _set_up_components(self, min_is_sleeptalking_threshold):
        """
        Set up objects, threads, and stop event required as well as pointer to where the snippets should be stored
        in memory before they are saved
        :param min_is_sleeptalking_threshold:
        :return:
        """
        self.snippets_queue = []
        self.stop_event = Event()
        self.file_handler = FileHandler()
        self.poller = SleeptalkPoller(min_is_sleeptalking_threshold=min_is_sleeptalking_threshold,
                                                snippets_queue=self.snippets_queue, stop_event=self.stop_event)
        self.processor = SleeptalkProcessor(self.file_handler, snippets_queue=self.snippets_queue,
                                                      stop_event=self.stop_event)
        self.poller_thread = None
        self.processor_thread = None
        self.scheduler_thread = None

    def run(self):
        self.t = Thread(target=self.run_schedule)
        self.t.start()

    def run_schedule(self):
        if self.force_recording:
            logging.info(f"Parameter --force-record is set")
            self.start_listening()
            try:
                while True:
                    time2.sleep(10)
            except KeyboardInterrupt:
                self.exit()
        else:
            # If the current time is in between start and stop time, this will not start otherwise
            start_time = datetime.strptime(self.start_time, '%H:%M').time()
            stop_time = datetime.strptime(self.stop_time, '%H:%M').time()
            local_time = datetime.now().time()
            logging.debug(f'Scheduled between {start_time} and {stop_time}. '
                         f'Current time is {local_time.strftime("%H:%M")}')
#            if (start_time < local_time < datetime.strptime('23:59', '%H:%M').time())\
 #                   or start_time > local_time and local_time < stop_time:
  #              logging.debug("Current time is within schedule, starting now")
  #              self.start_listening()
            schedule.every().day.at(self.start_time).do(self.start_listening)
            schedule.every().day.at(self.stop_time).do(self.stop_listening)
            try:
                while True:
                    schedule.run_pending()
                    time2.sleep(10)
            except KeyboardInterrupt:
                self.exit()

    def exit(self):
        schedule.clear()
        self.stop_listening()
        sys.exit(0)

    def start_listening(self):
        """
        Checks if we're already listenning and if not, starts everything up
        We create a new thread since threads can't be rerun
        :return:
        """
        if self.poller_thread and self.poller_thread.is_alive():
            logging.warning(f'Tried to start listenning, but somnilopy is already recording')
            return None
        else:
            self.stop_event.clear()
            self.poller_thread = Thread(target=self.poller.poll)
            self.processor_thread = Thread(target=self.processor.process_snippets)
            self.poller_thread.start()
            self.processor_thread.start()
            logging.info("Started Somnilopy")
            return True

    def stop_listening(self):
        """
        If we want to stop listening, try to exit our poller and processor threads cleanly. We want to exit cleanly
        just in case we are in the middle of recording or processing
        :return:
        """
        self.stop_event.set()
        if not self.poller_thread or not self.poller_thread.is_alive():
            return None
        self.poller_thread.join()
        self.processor_thread.join()
        return True

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
