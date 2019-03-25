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
    def __init__(self, folder, file_prefix):
        self.folder = folder
        self.file_prefix = file_prefix
        self.sample_width = pyaudio.get_sample_size(pyaudio.paInt16)
        self.loop = True

    def process_snippets(self, snippets_queue, stop_event, default_sleep_time=2):
        sleep_time = default_sleep_time
        while self.loop and not stop_event.is_set():
            if len(snippets_queue):
                snippet_tuple = snippets_queue.pop(0)
                self.write_to_file(snippet_tuple)
                sleep_time = default_sleep_time
            else:
                time.sleep(sleep_time)
        self.stop(snippets_queue)

    def write_to_file(self, snippet_tuple):
        snippet, timestamp = snippet_tuple
        file_name = f"{self.file_prefix}_{timestamp.strftime('%m-%d_%H-%M')}.wav"
        file_path = os.path.join(self.folder, file_name)
        snippet = pack('<' + ('h' * len(snippet)), *snippet)
        wf = wave.open(file_path, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.sample_width)
        wf.setframerate(44100)
        wf.writeframes(snippet)
        wf.close()
        logging.info(f"Saved snippet at {file_path}")

    def stop(self, snippets_queue):
        logging.info(f"Stopping SleeptalkProcessor, stop event set")
        if snippets_queue:
            for snippet_tuple in snippets_queue:
                self.write_to_file(snippet_tuple)
            logging.info(f"Wrote {len(snippets_queue)} to file")

