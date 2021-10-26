from flask import Flask, jsonify, request, url_for, make_response, abort
#from flask_api import status  # HTTP Status Codes

from werkzeug.exceptions import NotFound

from service.models import OrderItem, Order

from . import app
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

@app.route("/order/<int:order_id>/orderitem", methods=["POST"])
def create_item(order_id):
    """
    Creates an Order Item associated with an Order
    
    """
    app.logger.info("Request to create an order item")
    order = Order.find_or_404(order_id)
    orderItem = OrderItem()
    orderItem.deserialize(request.get_json())
    order.order_items.append(orderItem)
    #orderItem.create()
    order.save()
    message = orderItem.serialize()
    return make_response(jsonify(message))

@app.route("/order", methods=["POST"])
def create_order():
    """
    Creates an Order
    
    """
    app.logger.info("Request to create an order")
    #check_content_type("application/json")

    order = Order()
    order.deserialize(request.get_json())
    order.create()
    message = order.serialize()
    return make_response(jsonify(message))

    #return str(type(order.created_at))
    #"make_response(
    #    jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    #)"

@app.route("/order/<int:order_id>/orderitem/<int:item_id>", methods=["GET"])
def get_item(order_id, item_id):
    """
    Retrieve a single Order Item
    This endpoint will return a item based on it's id
    """
    app.logger.info("Request for order item with id: %s", item_id)
    orderitem = OrderItem.find_or_404(item_id)
    #return str(orderitem)
    return make_response(jsonify(orderitem.serialize()))

@app.route("/order/<int:order_id>", methods=["GET"])
def get_order(order_id):
    """
    Retrieve a single Order
    This endpoint will return a order based on it's id
    """
    app.logger.info("Request for order with id: %s", order_id)
    order = Order.find_or_404(order_id)
    #return str(order)
    return make_response(jsonify(order.serialize()))

@app.route("/order/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    """
    Delete an Order
    This endpoint will delete an Order based the id specified in the path
    """
    app.logger.info("Request to delete order with id: %s", order_id)
    order = Order.find(order_id)
    if order:
        order.delete()
    return make_response("deleted")

@app.route("/order/<int:order_id>/orderitem/<int:item_id>", methods=["DELETE"])
def delete_item(order_id, item_id):
    """
    Delete an Order Item
    This endpoint will delete an item based the id specified in the path
    """
    app.logger.info("Request to delete item with id: %s", item_id)
    item = OrderItem.find(item_id)
    if item:
        item.delete()
    return make_response("deleted item")

@app.route("/order", methods=["GET"])
def list_orders():
    """ Returns all of the Orders """
    app.logger.info("Request for Order list")
    orders = Order.all()
    results = [order.serialize() for order in orders]
    return make_response(jsonify(results))

@app.route("/order/<int:order_id>/orderitem", methods=["GET"])
def list_items(order_id):
    """ Returns all of the items for an Order """
    app.logger.info("Request for Order Item...")
    order = Order.find_or_404(order_id)
    results = [item.serialize() for item in order.order_items]
    return make_response(jsonify(results))

@app.route('/listorders')
def listorders():
    return str(Order.all())

@app.route('/listorderitems')
def listorderitems():
    """ Root URL response """
    return str(OrderItem.all())
