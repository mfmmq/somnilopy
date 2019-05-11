import logging
from datetime import datetime
import signal
import threading
from struct import pack
import wave
import os
import time
import pyaudio
import speech_recognition as sr
from soundfile import write as sf_write
from somnilopy.metadata import add_aiff_comment
import ipdb


class SleeptalkProcessor:
    def __init__(self, folder, file_prefix, to_text=True):
        self.folder = folder
        self.file_prefix = file_prefix
        self.sample_width = pyaudio.get_sample_size(pyaudio.paInt16)
        self.loop = True
        self.to_text = to_text
        if self.to_text:
            self.recognizer = sr.Recognizer()

    def process_snippets(self, snippets_queue, stop_event, sleep_time=2):
        while self.loop and not stop_event.is_set():
            if len(snippets_queue):
                snippet_tuple = snippets_queue.pop(0)
                file_path = self.write_to_aiff(snippet_tuple)
                if self.to_text:
                    text = self.speech2text(file_path)
                    add_aiff_comment(file_path, text)
            else:
                time.sleep(sleep_time)
        self.stop(snippets_queue)

    def speech2text(self, file_path):
        '''
        Takes a path to an audio file and a recognizer object 
        --> Applies speech recognition, returns result as string
        '''
        if not self.recognizer:
            self.recognizer = sr.Recognizer()
        try:
            file = sr.AudioFile(file_path)
        except AssertionError:
            lgging.info(f"Invalid audio file type for speech2text")
            return
        with file as source:
            audio = self.recognizer.record(source)
        return self.recognizer.recognize_sphinx(audio)

    def write_to_wav(self, snippet_tuple, to_text=False):
        snippet, timestamp = snippet_tuple
        file_name = f"{self.file_prefix}_{timestamp.strftime('%m-%d_%H-%M-%S')}.wav"
        file_path = os.path.join(self.folder, file_name)
        snippet = pack('<' + ('h' * len(snippet)), *snippet)
        wf = wave.open(file_path, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.sample_width)
        wf.setframerate(44100)
        wf.writeframes(snippet)
        wf.close()
        logging.info(f"Saved snippet at {file_path}")
        return file_path

    def write_to_aiff(self, snippet_tuple, to_text=False):
        snippet, timestamp = snippet_tuple
        file_name = f"{self.file_prefix}_{timestamp.strftime('%m-%d_%H-%M-%S')}.aiff"
        file_path = os.path.join(self.folder, file_name)
        sf_write(file_path, snippet, 44100)
        logging.info(f"Saved snippet at {file_path}")
        return file_path   

    def stop(self, snippets_queue):
        logging.info(f"Stopping SleeptalkProcessor, stop event set")
        if snippets_queue:
            for snippet_tuple in snippets_queue:
                self.write_to_file(snippet_tuple)
            logging.info(f"Wrote {len(snippets_queue)} to file")
