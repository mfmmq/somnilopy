import pyaudio
import logging
import time
from datetime import datetime
from array import array

from somnilopy import settings


class SleeptalkPoller:
    def __init__(self, min_snippet_time=2, max_silence_time=5, min_is_sleeptalking_threshold=200, prewindow=1,
                 snippets_queue=None, stop_event=None):
        self.stream = None
        # Variables to set up our thresholds
        self.prewindow = prewindow  # seconds
        self.min_snippet_time = min_snippet_time  # seconds
        self.max_silence_time = max_silence_time  # seconds
        self.min_is_sleeptalking_threshold = min_is_sleeptalking_threshold
        self.snippets_queue = [] if snippets_queue is None else snippets_queue
        self.stop_event = stop_event
        self.p = None

    def _setup_stream(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=settings.STREAM_AUDIO_FORMAT,
            channels=settings.STREAM_CHANNELS,
            rate=settings.STREAM_RATE,
            input=True,
            output=True,
            frames_per_buffer=settings.STREAM_CHUNK
        )

    def update_threshold(self, new_threshold):
        self.min_is_sleeptalking_threshold = new_threshold

    def start(self):
        if self.p and self.stream:
            return None
        else:
            self.poll()

    def poll(self):
        self._setup_stream()
        logging.info("Now recording!")
        snippet = array('h')

        # add a buffer to the start of the snippet
        while self.duration(snippet) < self.prewindow:
            data_chunk = array('h', self.stream.read(settings.STREAM_CHUNK))
            snippet.extend(data_chunk)

        self.reset_silence()  # start silence timer

        while self.stop_event and not self.stop_event.is_set():
            if self.is_sleeptalking_noise(data_chunk):
                self.reset_silence()  # restart silence timer
            if self.is_too_much_silence() and not self.is_sleeptalking_noise(snippet):
                snippet = array('h')  # fresh snippet
            elif self.is_sleeptalking_noise(snippet) and self.is_recording_sleeptalking(
                    snippet) and self.is_too_much_silence():
                # Move the snippet to another queue to be processed so we don't delay the recording thread
                # This is done in anticipation some audio processing has potential to take a while
                self.snippets_queue.append((snippet, datetime.now()))
                logging.info(f"Added snippet of sleeptalking length {len(snippet) / settings.STREAM_RATE:.2f} seconds")
                snippet = array('h')
                # add a buffer to the start of the snippet
                while self.duration(snippet) < self.prewindow:
                    data_chunk = array('h', self.stream.read(settings.STREAM_CHUNK))
                    snippet.extend(data_chunk)
                self.reset_silence()
            # extend snippet
            data_chunk = array('h', self.stream.read(settings.STREAM_CHUNK))
            snippet.extend(data_chunk)

        self.stop()

    @staticmethod
    def duration(array):
        return len(array) / settings.STREAM_RATE

    def is_sleeptalking_noise(self, night_noise):
        # If the data_chunk is loud enough to be sleeptalking, return True
        return max(night_noise) > self.min_is_sleeptalking_threshold

    def is_recording_sleeptalking(self, snippet):
        # If SleeptalkPoller is currently recording sleeptalking e.g. longer than the threshold,
        # return True
        return self.duration(snippet) > self.min_snippet_time

    def is_too_much_silence(self):
        # If the last few chunks have been silent for greater than max_silence_time, return True
        return self.silence_length() > self.max_silence_time

    def reset_silence(self):
        self.silence_start = time.time()

    def silence_length(self):
        return time.time() - self.silence_start

    def is_end(self):
        return 0

    def stop(self):
        """
        This will not save the current snippet, needs some updating
        :return:
        """
        if self.p:
            if self.stream and self.stream.is_active():
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            else:
                return None
            self.p.terminate()
            self.p = None
        logging.info("Stopping SleeptalkPoller, stop event set")
