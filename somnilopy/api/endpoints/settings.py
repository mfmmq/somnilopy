import logging
from flask_restplus import Resource
from somnilopy.api.restplus import api
from flask import current_app as app
from flask import Response


settings_ns = api.namespace('settings', description='Endpoints for checking and updating recording settings')


@settings_ns.route('/status')
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
