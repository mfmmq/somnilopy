import time
from array import array
import logging
from somnilopy import settings


class Sound:
    def __init__(self):
        self.array = array('h')
        self.silence_start = time.time()
    #
    # def process(self, stream):
    #     while self.length < settings.PREWINDOW:
    #         return

    def add_buffer(self, chunk):
        chunk = array('h', chunk)
        self.check_if_sleeptalking(chunk)
        self.array.extend(chunk)

    @property
    def length(self):
        return len(self.array) / settings.STREAM_RATE

    def check_if_sleeptalking(self, chunk):
        # If the data_chunk is loud enough to be sleeptalking, return True
        if max(chunk) > settings.SLEEPTALKING_VOL_THRESHOLD:
            logging.debug(f'Max chunk is {max(chunk)}')
            self.silence_start = time.time()
            return True
        else:
            return False

    @property
    def done_recording(self):
        return self._is_loud_enough and self.is_long_enough and self._tail_is_too_silent

    @property
    def is_silent(self):
        if self._tail_is_too_silent and not self._is_loud_enough:
            logging.debug(f'Sound is silent --  too long of a silent tail and not loud enough: {self._tail_is_too_silent} {self._is_loud_enough}')
            logging.debug(f'Length is {self.length}')
            return True
        return False

    @property
    def _is_loud_enough(self):
        # If the data_chunk is loud enough to be sleeptalking, return True
        return max(self.array) > settings.SLEEPTALKING_VOL_THRESHOLD

    @property
    def is_long_enough(self):
        # If SleeptalkPoller is currently recording sleeptalking e.g. longer than the threshold,
        # return True
        return self.length > settings.MIN_LENGTH

    @property
    def _tail_is_too_silent(self):
        # If the last few chunks have been silent for greater than max_silence_time, return True
        return self.tailing_silence_time > settings.MAX_SILENCE_TIME

    @property
    def tailing_silence_time(self):
        return time.time() - self.silence_start

    def is_end(self):
        return 0
