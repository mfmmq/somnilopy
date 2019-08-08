import pyaudio


# Flask settings
FLASK_SERVER_NAME = '192.168.0.18:5000'
FLASK_DEBUG = False  # Do not use debug mode in production

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False

# Audio stream settings
STREAM_CHUNK = 5000
STREAM_AUDIO_FORMAT = pyaudio.paInt16
STREAM_CHANNELS = 1
STREAM_RATE = 44100

# Somnilopy settings
LABELS = ['is-sleeptalking', 'not-sleeptalking', 'autosave', 'delete']