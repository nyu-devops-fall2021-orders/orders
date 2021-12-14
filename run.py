"""
This file runs the Flask app for the server
"""

import sys
from service import APP
from service import routes

APP.logger.info("Starting with DATABASE_URI=%s", APP.config['DATABASE_URI'])

try:
    routes.common.init_db()  # make our sqlalchemy tables
except Exception as error:  # pylint: disable=broad-except
    # gunicorn requires exit code 4 to stop spawning workers when they die
    sys.exit(4)

APP.logger.info(80 * '*')
APP.logger.info('   O R D E R    S E R V I C E    R U N N I N G   '.center(80, '*'))
APP.logger.info(80 * '*')

APP.logger.info('Service inititalized!')
