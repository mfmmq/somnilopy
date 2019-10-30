import logging
import os
import time
import pyaudio
import speech_recognition as sr
from soundfile import write as sf_write

from somnilopy import settings


class SleeptalkProcessor:
    def __init__(self, file_handler, to_text=True, snippets_queue=None, stop_event=None):
        self.file_handler = file_handler
        self.sample_width = pyaudio.get_sample_size(settings.STREAM_AUDIO_FORMAT)
        self.loop = True
        self.to_text = to_text
        self.recognizer = sr.Recognizer()
        self.snippets_queue = [] if snippets_queue is None else snippets_queue
        self.stop_event = stop_event

    def process_snippets(self, sleep_time=2):
        while self.loop and not self.stop_event.is_set():
            if len(self.snippets_queue):
                snippet_tuple = self.snippets_queue.pop(0)
                file_path = self.save_snippet(snippet_tuple)
                if self.to_text:
                    text = self.speech2text(file_path)
                    if text:
                        self.file_handler.update_comment_from_path(file_path, text)
                    else:
                        logging.debug(f"No speech detected for file at {file_path}")
            else:
                time.sleep(sleep_time)
        self.stop(self.snippets_queue)

    def speech2text(self, file_path):
        """
        Takes a path to an audio file and a recognizer object 
        --> Applies speech recognition, returns result as string if speech is recognised, None if not
        """
        try:
            file = sr.AudioFile(file_path)
        except AssertionError:
            logging.info(f"Invalid audio file type for speech2text")
            return None
        with file as source:
            try:
                audio = self.recognizer.record(source)
                return self.recognizer.recognize_sphinx(audio)
            except sr.UnknownValueError:
                return None

    def save_snippet(self, snippet_tuple):
        snippet, timestamp = snippet_tuple
        file_name = f"{self.file_handler.file_prefix}_{timestamp.strftime('%m-%d_%H-%M-%S')}.flac"
        file_path = os.path.join(self.file_handler.folder, 'autosave', file_name)
        sf_write(file_path, snippet, settings.STREAM_RATE)
        logging.info(f"Saved snippet at {file_path}")
        return file_path   

    def stop(self, snippets_queue):
        logging.info(f"Stopping SleeptalkProcessor, stop event set")
        if snippets_queue:
            for snippet_tuple in snippets_queue:
                self.save_snippet(snippet_tuple)
            logging.info(f"Wrote {len(snippets_queue)} to file")
