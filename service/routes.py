from . import app
from flask import Flask, jsonify#, request, url_for, make_response, abort
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