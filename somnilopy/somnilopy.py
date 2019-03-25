import time
import schedule
import logging
from threading import Thread, Event
from somnilopy.sleeptalk_processor import SleeptalkProcessor
from somnilopy.sleeptalk_poller import SleeptalkPoller


class Somnilopy:
    def __init__(self, input_schedule, force_recording, folder, file_name):
        self.snippets_queue = []
        self.folder = folder
        self.file_name = file_name
        self.force_recording = force_recording
        self.stop_event = Event()

        self.start_time, self.stop_time = input_schedule.split('>')

        self.sleeptalk_poller = SleeptalkPoller(self.force_recording)
        self.sleeptalk_processor = SleeptalkProcessor(self.folder, self.file_name)
        self.t_poller = None
        self.t_processor = None

    def run(self):
        if self.force_recording:
            logging.info(f"Parameter --force-record is set")
            self.start_listening()
            try:
                while True:
                    time.sleep(10)
            except KeyboardInterrupt:
                self.exit()
        else:
            '''
            If the current time is in between start and stop time, this will not start otherwise
            '''
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

    def start_listening(self):
        self.stop_event.clear()
        self.t_poller = Thread(target=self.sleeptalk_poller.listen_for_snippets,
                               args=(self.snippets_queue, self.stop_event))
        self.t_processor = Thread(target=self.sleeptalk_processor.process_snippets,
                                  args=(self.snippets_queue, self.stop_event))
        self.t_poller.start()
        self.t_processor.start()
        logging.info("Started Somnilopy")

    def stop_listening(self):
        self.stop_event.set()
        if self.t_poller:
            '''
            Reset to None to handle edge case if KeyboardInterupt is received, but threads have not been running
            '''
            self.t_poller.join()
            self.t_poller = None
        if self.t_processor:
            self.t_processor.join()
            self.t_processor = None
        logging.info("Stopped Somnilopy")


