from threading import Thread
from somnilopy.sleeptalk_processor import SleeptalkProcessor
from somnilopy.sleeptalk_poller import SleeptalkPoller




class Somnilopy:
    def __init__(self):
        self.snippets_queue = []
        self.folder = 'autosave'
        self.sleeptalk_poller = SleeptalkPoller()
        self.sleeptalk_processor = SleeptalkProcessor(self.folder)
        self.t_poller = Thread(target=self.sleeptalk_poller.listen_for_snippets, args=(self.snippets_queue,))
        self.t_processor = Thread(target=self.sleeptalk_processor.process_snippets, args=(self.snippets_queue,))
        self.start_listening()


    def start_listening(self):
        self.t_poller.start()
        self.t_processor.start()

    def stop_listening(self):
        self.t_poller.join()
        self.t_processor.join()

