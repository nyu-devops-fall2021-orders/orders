from . import app
from flask import Flask, jsonify, request#, url_for, make_response, abort
from service.models import OrderItem, Order
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
    OrderItem.init_db(app)
    Order.init_db(app)

@app.route("/createitem", methods=["POST"])
def create_item():
    """
    Creates a Pet
    This endpoint will create a Pet based the data in the body that is posted
    """
    app.logger.info("Request to create an order")
    orderItem = OrderItem()
    orderItem.deserialize(request.get_json())
   
    return str(orderItem.price)

@app.route("/create", methods=["POST"])
def create_order():
    """
    Creates a Pet
    This endpoint will create a Pet based the data in the body that is posted
    """
    app.logger.info("Request to create an order")
    #check_content_type("application/json")

    order = Order()
    order.deserialize(request.get_json())
    order.create()
    
    return str(order.updated_at)

    #return str(type(order.created_at))
    #"make_response(
    #    jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    #)"