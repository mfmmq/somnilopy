import logging
import threading
from flask_restplus import Resource
from somnilopy.api.restplus import api
from flask import current_app as app
from flask import Response


recording_ns = api.namespace('recording', description='Endpoints for checking and controlling recording status')


@recording_ns.route('/status')
class RecordingCollection(Resource):
    def get(self):
        """
        Get the current status, ie whether somnilopy is currently recording or not
        :return:
        """
        if app.recorder.poller.stream and app.recorder.poller.stream.is_active():
            return True
        else:
            return False


@recording_ns.route('/start')
class RecordingControlStart(Resource):
    def post(self):
        """
        Start recording
        :return:
        """
        if app.recorder.poller.stream and app.recorder.poller.stream.is_active():
            return Response('Already recording', 201)
        else:
            app.recorder.exit()
            logging.info('Recorder exited')
            app.t.join()
            logging.info('Thread joined')
            app.t = threading.Thread(target=app.recorder.run)
            app.t.start()
            return Response('Now recording', 200)


@recording_ns.route('/stop')
class RecordingControlStop(Resource):
    def post(self):
        """
        Stop recording
        :return:
        """
        response = app.recorder.stop_listening()
        if response is None:
            return Response('Tried to stop recording, but already not recording', 201)
        else:
            return Response('Stopped recording', 200)

