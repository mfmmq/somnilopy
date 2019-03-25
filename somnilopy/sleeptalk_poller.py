import sys
import pyaudio
import logging
import signal
import threading
import time
from datetime import datetime
from array import array


class SleeptalkPoller:
    def __init__(self, force, min_snippet_time=1, max_silence_time=1, min_is_sleeptalking_threshold=600):

        # Variables to set up our stream
        self.chunk = 5000
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.p = pyaudio.PyAudio()
        self.stream = None

        # Variables to set up our thresholds
        self.min_snippet_time = min_snippet_time  # seconds
        self.max_silence_time = max_silence_time  # seconds
        self.min_is_sleeptalking_threshold = min_is_sleeptalking_threshold


    def listen_for_snippets(self, snippets_queue, stop_event):
        self.stream = self.p.open(
            format=self.audio_format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            output=True,
            frames_per_buffer=self.chunk
        )

        logging.info("Now recording!")
        silent_counter = 1

        snippet = array('h')
        while not stop_event.is_set():
            data_chunk = array('h', self.stream.read(self.chunk))
            if self.is_sleeptalking_noise(data_chunk):
                if self.is_recording_sleeptalking(snippet):
                    logging.info("Started new recording")
                snippet.extend(data_chunk)
                silent_counter = 0
            else:
                silent_counter += 1
            if self.is_too_much_silence(silent_counter) and not self.is_recording_sleeptalking(snippet):
                # Reset snippet and start anew so we don't have loads of silence in our recordings
                snippet = array('h')
            if self.is_recording_sleeptalking(snippet) and self.is_too_much_silence(silent_counter):
                # Move the snippet to another queue to be processed so we don't delay the recording thread
                # This is done in anticipation some audio processing has potential to take a while
                snippets_queue.append((snippet, datetime.now()))
                logging.info(f"Added snippet of sleeptalking length {len(snippet) / self.rate} seconds")
                snippet = array('h')

        self.stop()

    def is_sleeptalking_noise(self, night_noise):
        # If the data_chunk is loud enough to be sleeptalking, return True
        return max(night_noise) > self.min_is_sleeptalking_threshold

    def is_recording_sleeptalking(self, snippet):
        # If SleeptalkPoller is currently recording sleeptalking e.g. longer than the threshold,
        # return True
        return len(snippet) / self.rate > self.min_is_sleeptalking_threshold

    def is_too_much_silence(self, silent_counter):
        # If the last few chunks have been silent for greater than max_silence_time, return True
        return silent_counter*self.chunk/self.rate > self.max_silence_time

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
