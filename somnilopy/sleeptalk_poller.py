import pyaudio
import logging
import time
from datetime import datetime
from array import array

STREAM_CHUNK = 5000
STREAM_AUDIO_FORMAT = pyaudio.paInt16
STREAM_CHANNELS = 1
STREAM_RATE = 44100


class SleeptalkPoller:
    def __init__(self, min_snippet_time=1, max_silence_time=1, min_is_sleeptalking_threshold=600, prewindow=1):

        # Variables to set up our thresholds
        self.prewindow = prewindow # seconds
        self.min_snippet_time = min_snippet_time  # seconds
        self.max_silence_time = max_silence_time  # seconds
        self.min_is_sleeptalking_threshold = min_is_sleeptalking_threshold

    def _setup_stream(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=STREAM_AUDIO_FORMAT,
            channels=STREAM_CHANNELS,
            rate=STREAM_RATE,
            input=True,
            output=True,
            frames_per_buffer=STREAM_CHUNK
        )

    def listen_for_snippets(self, snippets_queue, stop_event):
        self._setup_stream()
        logging.info("Now recording!")
        snippet = array('h')

        # add a buffer to the start of the snippet
        while self.duration(snippet) < self.prewindow:
            data_chunk = array('h', self.stream.read(STREAM_CHUNK))
            snippet.extend(data_chunk)

        self.reset_silence() # start silence timer

        while not stop_event.is_set():
            if self.is_sleeptalking_noise(data_chunk):
                self.reset_silence() # restart silence timer
            if self.is_too_much_silence() and not self.is_sleeptalking_noise(snippet):
                snippet = array('h') # fresh snippet
            elif self.is_sleeptalking_noise(snippet) and self.is_recording_sleeptalking(snippet) and self.is_too_much_silence():
                # Move the snippet to another queue to be processed so we don't delay the recording thread
                # This is done in anticipation some audio processing has potential to take a while
                snippets_queue.append((snippet, datetime.now()))
                logging.info(f"Added snippet of sleeptalking length {len(snippet)/STREAM_RATE:.2f} seconds")
                snippet = array('h')
                # add a buffer to the start of the snippet
                while self.duration(snippet) < self.prewindow:
                    data_chunk = array('h', self.stream.read(STREAM_CHUNK))
                    snippet.extend(data_chunk)
                self.reset_silence()
            # extend snippet
            data_chunk = array('h', self.stream.read(STREAM_CHUNK))
            snippet.extend(data_chunk)

        self.stop()

    @staticmethod
    def duration(array):
        return len(array) / STREAM_RATE

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
        '''
        This will not save the current snippet, needs some updating
        :return:
        '''
        if self.stream.is_active():
            self.stream.stop_stream()
        self.p.terminate()
        logging.debug("Stopping SleeptalkPoller, stop event set")
