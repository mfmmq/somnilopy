import logging
from flask import Flask
from flask_restplus import Api
from somnilopy import settings


api = Api(version='1.0', title='somnilopy API', description='somnilopy Flask API endpoint')


@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    logging.exception(message)

    if not settings.FLASK_DEBUG:
        return {'message': message}, 500


