import logging
from flask import Flask, Blueprint
from flask_cors import CORS
from somnilopy.api.endpoints.files import files_ns
from somnilopy.api.endpoints.recording import recording_ns
from somnilopy.api.restplus import api
from somnilopy import settings
import threading


class Backend:
    def __init__(self, recorder, server_name):
        self.app = Flask(__name__)
        self.app.recorder = recorder
        self.run_recorder()
        self.configure_app(server_name)
        self.initialize_app()
        CORS(self.app)

    def run(self):
        """
        Set up and run the back-end api for the frond-end that serves webpages and static files
        :param start_time:
        :param stop_time:
        :return:
        """
        logging.info(f'Starting up api at http://{settings.FLASK_SERVER_NAME}/api')
        self.app.run()
        self.app.t.join()

    def configure_app(self, server_name):
        self.app.config['SERVER_NAME'] = server_name if server_name else settings.FLASK_SERVER_NAME
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

    def run_recorder(self):
        self.app.t = threading.Thread(target=self.app.recorder.run)
        self.app.t.start()
