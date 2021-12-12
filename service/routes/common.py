"""
This module contains the common routes and utility functions for the Orders microservice.

"""
from flask_restx import Api
from service import APP, status
from service.models import DataValidationError, DatabaseConnectionError, Order, Item

@APP.route('/')
def index():
    """ Root URL response """
    return APP.send_static_file("index.html")


######################################################################
# Configure Swagger
######################################################################

API = Api(APP,
          version='1.0.0',
          title='Orders REST API Service',
          description='Serving the API for the Orders microservice at NYU DevOps 2021.',
          default='orders',
          default_label='Orders microservice',
          doc='/apidocs',
          prefix='/api'
          )

######################################################################
# Special Error Handlers
######################################################################


@API.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    message = str(error)
    APP.logger.error(message)
    return {
        'status_code': status.HTTP_400_BAD_REQUEST,
        'error': 'Bad Request',
        'message': message
    }, status.HTTP_400_BAD_REQUEST


@API.errorhandler(DatabaseConnectionError)
def database_connection_error(error):
    """ Handles Database Errors from connection attempts """
    message = str(error)
    APP.logger.critical(message)
    return {
        'status_code': status.HTTP_503_SERVICE_UNAVAILABLE,
        'error': 'Service Unavailable',
        'message': message
    }, status.HTTP_503_SERVICE_UNAVAILABLE

######################################################################
###########      U T I L I T Y    F U N C T I O N S      #############
######################################################################


def init_db():
    """ Initializes the SQLAlchemy app """
    Item.init_db(APP)
    Order.init_db(APP)


def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    APP.logger.error(message)
    API.abort(error_code, message)
