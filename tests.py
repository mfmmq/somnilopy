import unittest
import array
import numpy
from somnilopy.sleeptalk_poller import SleeptalkPoller


class TestSleeptalkPoller(unittest.TestCase):
    def setUp(self):
        # Set reasonable thresholds
        self.min_snippet_time = 2
        self.max_silence_time = 2
        self.min_is_sleeptalking_threshold = 300

    def create_fake_array(self, sleeptalk_poller, time=1):
        amplitude = 2^sleeptalk_poller.audio_format
        x = numpy.arrange(sleeptalk_poller.rate)
        snippet = array('h', amplitude*numpy.sin(2*numpy.pi*x*time))



    def test_is_sleeptalking_noise(self):
        sleeptalk_poller = SleeptalkPoller(self.min_snippet_time,
                                           self.max_silence_time,
                                           self.min_is_sleeptalking_threshold)

        sleeptalk_poller.is_sleeptalking_noise(snippet)