import pyaudio
import logging
import threading
import signal
import sys
from flask import Flask
from flask_restful import Resource, Api
from somnilopy.sleeptalk_poller import SleeptalkPoller
from somnilopy.sleeptalk_processor import SleeptalkProcessor
from somnilopy.somnilopy import Somnilopy


def setup_logging():
    logging.basicConfig(format="%(asctime)s - %(levelname)s [%(filename)s] - %(message)s",
                        level=logging.DEBUG)


if __name__ == "__main__":

    setup_logging()
    snippets_queue = []
    somnilopy = Somnilopy()


    '''
    Should probably be turned into an api to be useful
    Endpoints might include something to get all info about tracks 
    also might need to include a delete endpoint to delete tracks
    or a put endpoint to move certain tracks to 'saved' or a way to download tracks..
    Need to think of a way to stream tracks with a front-end and how that will integrate with python...
    Maybe react.js?
    '''
    #app = Flask(__name__)
    #api = Api(app)

    #api.add_resource(Somnilopy, '/')



