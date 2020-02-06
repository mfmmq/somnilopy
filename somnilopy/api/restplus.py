import logging
from flask import Flask
from flask_restplus import Api, cors
from somnilopy import settings
from somnilopy.exceptions import *

api = Api(version='1.0', title='somnilopy API', description='somnilopy Flask API endpoint', validate=True)


@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    logging.exception(message)
    if not settings.FLASK_DEBUG:
        return {'message': message}, 500


@api.errorhandler(FileNotFoundError)
def file_not_found_error_handler(e):
    message = 'File not found'
    logging.exception(message)
    if not settings.FLASK_DEBUG:
        return {'message': message}, 404


@api.errorhandler(LabelNotAllowedError)
def file_not_found_error_handler(e):
    message = 'Label not allowed. Is it enabled in calibration.py?'
    logging.exception(message)
    if not settings.FLASK_DEBUG:
        return {'message': message}, 404
