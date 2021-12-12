"""
This is the main package where the data models and business logic lie.
"""

import logging
from flask import Flask
from flask.logging import create_logger

APP = Flask(__name__)
APP.logger = create_logger(APP)
APP.config.from_object("config")

# Set up logging for production
APP.logger.propagate = False
print(f"Setting up logging for {__name__}...")
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    if gunicorn_logger:
        APP.logger.handlers = gunicorn_logger.handlers
        APP.logger.setLevel(gunicorn_logger.level)
