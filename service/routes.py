from . import app
from flask import Flask, jsonify#, request, url_for, make_response, abort
from service.models import Order
#@app.route('/index')
@app.route('/')

def index():
    """ Root URL response """
    return "Hello, World"#(
        #jsonify(
            #name="Pet Demo REST API Service",
            #version="1.0",
            #paths=url_for("list_pets", _external=True),
        #),
        #status.HTTP_200_OK,
    #)

def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Order.init_db(app)
