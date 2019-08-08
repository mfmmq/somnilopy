import logging
from flask import Response, jsonify, request, send_file, abort, Flask
from flask_restplus import Api, Resource
from somnilopy.api.restplus import api


recording_ns = api.namespace('recording', description='Endpoints for checking recording status')

@recording_ns.route('/')
class RecordingCollection(Resource):
    def get(self):
        '''
        Get the current status, ie whether somnilopy is currently recording or not
        :return:
        '''
        return None


@recording_ns.route('/start')
class RecordingControlStart(Resource):
    def post(self):
        '''
        Start recording
        :return:
        '''
        return None


@recording_ns.route('/stop')
class RecordingControlStop(Resource):
    def post(self):
        '''
        Stop recording
        :return:
        '''
        return None
