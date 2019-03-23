import logging
from datetime import datetime
import signal
import threading
from struct import pack
import wave
import os
import time
import pyaudio


class SleeptalkProcessor:
    def __init__(self, folder='autosave'):
        self.folder = folder
        self.sample_width = pyaudio.get_sample_size(pyaudio.paInt16)
        self.queue_snapshot = []

    def process_snippets(self, snippets_queue):
        sleep_time = 2
        while True:
            if len(snippets_queue):
                snippet = snippets_queue.pop(0)
                self.write_to_file(snippet)
                sleep_time = 2
            else:
                time.sleep(sleep_time)
                sleep_time += 10

    def write_to_file(self, snippet):
        file_name = f"autosave_{datetime.now().strftime('%m-%d_%H-%M')}.wav"
        file_path = os.path.join(self.folder, file_name)
        snippet = pack('<' + ('h' * len(snippet)), *snippet)
        wf = wave.open(file_path, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.sample_width)
        wf.setframerate(44100)
        wf.writeframes(snippet)
        wf.close()
        logging.info(f"Saved snippet at {file_path}")



