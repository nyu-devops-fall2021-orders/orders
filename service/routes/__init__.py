"""
This package contains all the API route definitions for the Orders microservice
"""

from . import common, orders, items

common.APP.logger.info("Initialized routes for %s", orders.__name__)
common.APP.logger.info("Initialized routes for %s", items.__name__)
