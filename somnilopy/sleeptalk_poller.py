import pyaudio
import logging
from datetime import datetime

from somnilopy.handlers.stream_handler import Sound
from somnilopy import settings


class SleeptalkPoller:
    def __init__(self, stop_event=None):
        self.stream = None
        self.stop_event = stop_event
        self.p = None
        self.current_consumer = None

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

    def poll(self):
        self._setup_stream()
        logging.info("Now recording!")
        sound = Sound()

        self.current_consumer.send(None)  # Start consumer
        try:
            while not self.stop_event.is_set():
                while not sound.is_long_enough:
                    sound.add_buffer(self.stream.read(settings.STREAM_CHUNK))
                if sound.is_silent:
                    sound = Sound()
                elif sound.done_recording:
                    logging.info(f"Recorded sleeptalking of length {sound.length:.2f} seconds")
                    self.current_consumer.send((sound, datetime.now()))
                    sound = Sound()
                sound.add_buffer(self.stream.read(settings.STREAM_CHUNK))
        except OSError:
            pass

    def stop(self):
        """
        This will not save the current snippet, needs some updating
        :return:
        """
        if self.current_consumer:
            self.current_consumer.close()
        if self.p:
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
            self.stream = None
            self.p = None

        logging.info("Stopping SleeptalkPoller, stop event set")
