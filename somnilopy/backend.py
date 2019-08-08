import logging
from datetime import datetime
from flask import Flask, jsonify, Response, send_file, abort, Blueprint
from flask_cors import CORS
from flask_restful import Resource
from somnilopy.api.endpoints.files import files_ns
from somnilopy.api.endpoints.recording import recording_ns
from somnilopy.api.restplus import api
from somnilopy import settings


class Backend:
    def __init__(self):
        self.app = Flask(__name__)
        self.configure_app()
        self.initialize_app()

    def run(self):
        '''
        Set up and run the back-end api for the frond-end that serves webpages and static files
        :param start_time:
        :param stop_time:
        :return:
        '''
        logging.info('Starting up api')
        self.app.run()

    def configure_app(self):
        self.app.config['SERVER_NAME'] = settings.FLASK_SERVER_NAME
        self.app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
        self.app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
        self.app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
        self.app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP

    def initialize_app(self):
        blueprint = Blueprint('api', __name__, url_prefix='/api')
        api.init_app(blueprint)
        api.add_namespace(files_ns)
        api.add_namespace(recording_ns)
        self.app.register_blueprint(blueprint)

