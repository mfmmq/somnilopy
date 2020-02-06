import time
from array import array

from somnilopy import settings


class Sound:
    def __init__(self):
        self.array = array('h')
        self.silence_start = time.time()

    def process(self):
        return

    def add_buffer(self, chunk):
        chunk = array('h', chunk)
        self.check_if_sleeptalking(chunk)
        self.array.extend(chunk)

    @property
    def duration(self):
        return len(self.array) / settings.STREAM_RATE

    def check_if_sleeptalking(self, chunk):
        # If the data_chunk is loud enough to be sleeptalking, return True
        if max(chunk) > settings.SLEEPTALKING_VOL_THRESHOLD:
            self.silence_start = time.time()
            return True
        else:
            return False

    @property
    def still_recording(self):
        return True

    @property
    def done_recording(self):
        return self._is_loud_enough and self._is_long_enough and self._tail_is_too_silent

    @property
    def is_silent(self):
        return self._tail_is_too_silent and not self._is_loud_enough

    @property
    def _is_loud_enough(self):
        # If the data_chunk is loud enough to be sleeptalking, return True
        return max(self.array) > settings.SLEEPTALKING_VOL_THRESHOLD

    @property
    def _is_long_enough(self):
        # If SleeptalkPoller is currently recording sleeptalking e.g. longer than the threshold,
        # return True
        return self.duration > settings.MIN_SNIPPET_TIME

    @property
    def _tail_is_too_silent(self):
        # If the last few chunks have been silent for greater than max_silence_time, return True
        return self.tailing_silence_time > settings.MAX_SILENCE_TIME

    @property
    def tailing_silence_time(self):
        return time.time() - self.silence_start

    def is_end(self):
        return 0
