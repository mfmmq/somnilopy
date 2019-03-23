import sys
import pyaudio
import logging
import signal
import threading
import time
from datetime import datetime
from array import array


class SleeptalkPoller:
    def __init__(self, schedule="00:00>6:30", force=True):
        self.chunk = 5000
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.force_record = force
        start, stop = schedule.split('>')
        self.start_time = time.strptime(start, '%H:%M')
        self.stop_time = time.strptime(stop, '%H:%M')


    def listen_for_snippets(self, snippets_queue):
        self.stream = self.p.open(
            format=self.audio_format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            output=True,
            frames_per_buffer=self.chunk
        )

        logging.info("Now recording!")
        talking_counter = 0
        silent_counter = 1

        snippet = array('h')
        while True:
            if self.is_scheduled(time.localtime()) or self.force_record:
                data_chunk = array('h', self.stream.read(self.chunk))
                if self.is_sleeptalking(data_chunk):
                    if talking_counter == self.t_recording:
                        logging.info("Started new recording")
                    snippet.extend(data_chunk)
                    silent_counter = 0
                else:
                    silent_counter += 1
                if silent_counter*self.chunk/self.rate > self.t_silent and len(snippet)/self.rate < self.t_recording:
                    snippet = array('h')
                if len(snippet)/self.rate > self.t_recording and silent_counter*self.chunk/self.rate > self.t_silent:
                    snippets_queue.append(snippet)
                    logging.info(f"Added snippet of sleeptalking length {len(snippet) / self.rate} seconds")
                    snippet = array('h')
            else:
                time.sleep(20)

    @property
    def t_recording(self):
        # threshold for minimum length of recording
        return 1

    @property
    def t_silent(self):
        # threshold for maximum silence -- silence must be shorter than this, else recording stops
        return 1

    @staticmethod
    def is_sleeptalking(night_noise):
        threshold = 600
        if max(night_noise) > threshold:
            return True
        return False

    def start(self):
        self.stream.start()

    def stop(self):
        if self.stream.is_active():
            self.stream.stop_stream()

    def exit(self):
        self.stop()
        self.p.terminate()
        logging.debug("Exited SleeptalkPoller cleanly")
        return 0

    def is_scheduled(self, current_time):
        if self.start_time < current_time < self.stop_time:
            return True
        else:
            return False
