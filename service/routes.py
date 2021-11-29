from flask import jsonify, request, url_for, make_response
from . import status  # HTTP Status Codes

from service.models import OrderItem, Order, OrderStatus

from . import app

@app.route('/')
def index():
    """ Root URL response """
    return app.send_static_file("index.html")
    # return (
    #     jsonify(
    #         name="Orders REST API Service",
    #         version="1.0",
    #     ),
    #     status.HTTP_200_OK,
    # )

def init_db():
    """ Initializes the SQLAlchemy app """
    global app
    OrderItem.init_db(app)
    Order.init_db(app)

######################################################################
# CREATE AN ORDER ITEM
######################################################################
@app.route("/order/<int:order_id>/orderitem", methods=["POST"])
def create_item(order_id):
    """
    Creates an Order Item associated with an Order
    
    """
    app.logger.info("Request to create an order item")
    order = Order.find_or_404(order_id)
    
    orderItem = OrderItem()
    orderItem.deserialize(request.get_json())
    orderItem.create()
    
    order.order_items.append(orderItem)
    order.update()
    message = orderItem.serialize()
    return make_response(
        jsonify(message), status.HTTP_201_CREATED
    )

######################################################################
# FETCH AN ORDER ITEM
######################################################################
@app.route("/order/<int:order_id>/orderitem/<int:item_id>", methods=["GET"])
def get_item(order_id, item_id):
    """
    Retrieve a single Order Item
    This endpoint will return a item based on it's id
    """
    app.logger.info("Request for order item with id: %s", item_id)
    _ = Order.find_or_404(order_id)
    orderItem = OrderItem.find_or_404(item_id)
    return make_response(
        jsonify(orderItem.serialize())
    )

######################################################################
# LIST ALL ORDER ITEMS FOR AN ORDER
######################################################################
@app.route("/order/<int:order_id>/orderitem", methods=["GET"])
def list_items(order_id):
    """ Returns all of the items for an Order """
    app.logger.info("Request for Order Item...")
    order = Order.find_or_404(order_id)
    results = [item.serialize() for item in order.order_items]
    return make_response(jsonify(results))

######################################################################
# LIST ALL ORDER ITEMS
######################################################################
@app.route('/listorderitems')
def listorderitems():
    """ Root URL response """
    order_items = []
    for order_item in OrderItem.all():
        order_items.append(OrderItem.serialize(order_item))
    
    return make_response(jsonify(order_items))

######################################################################
# UPDATE AN EXISTING ORDER ITEM
######################################################################
@app.route("/order/<int:order_id>/orderitem/<int:item_id>", methods=["PUT"])
def update_item(order_id, item_id):
    """
    Update an Order Item
    This endpoint will update an Order Item based the body that is posted
    """
    app.logger.info("Request to update order item with order_id: %s, and item_id: %s", order_id, item_id)
    _ = Order.find_or_404(order_id)
    orderItem = OrderItem.find_or_404(item_id)
    orderItem.deserialize(request.get_json())
    orderItem.id = item_id
    orderItem.order_id = order_id
    orderItem.update()
    return make_response(
        jsonify(orderItem.serialize()), status.HTTP_200_OK
    )

######################################################################
# DELETE AN ORDER ITEM
######################################################################
@app.route("/order/<int:order_id>/orderitem/<int:item_id>", methods=["DELETE"])
def delete_item(order_id, item_id):
    """
    Delete an Order Item
    This endpoint will delete an item based the id specified in the path
    """
    app.logger.info("Request to delete item with order_id: %s and item_id: %s", order_id, item_id)

    _ = Order.find_or_404(order_id)
    item = OrderItem.find(item_id)
    if item:
        item.delete()
    return make_response("", status.HTTP_204_NO_CONTENT)

######################################################################
# CREATE AN ORDER
######################################################################
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
    return make_response(
        jsonify(message), status.HTTP_201_CREATED
    )

######################################################################
# FETCH AN ORDER
######################################################################
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

######################################################################
# LIST ALL ORDERS
######################################################################
@app.route("/order", methods=["GET"])
def list_orders():
    """ Returns all of the Orders """
    app.logger.info("Request for Order list")
    status = request.args.get("status")
    customer_id_str = request.args.get("customer-id")
    if status:
        orders = Order.find_by_status(OrderStatus[status])
    elif customer_id_str:
        orders = Order.find_by_customer(int(customer_id_str))
    else:
        orders = Order.all()
    results = [order.serialize() for order in orders]
    return make_response(jsonify(results))

######################################################################
# UPDATE AN EXISTING ORDER
######################################################################
@app.route("/order/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    """
    Update an Order Item
    This endpoint will update an Order Item based the body that is posted
    """
    app.logger.info("Request to update order with order_id: %s", order_id)
    order = Order.find_or_404(order_id)
    data = request.get_json()
    if "order_items" in data:
        del data["order_items"]
    order.deserialize(data)
    
    order.id = order_id
    order.update()
    return make_response(
        jsonify(order.serialize()), status.HTTP_200_OK
    )

######################################################################
# ACTION TO CANCEL AN EXISTING ORDER
######################################################################
@app.route("/order/<int:order_id>/cancel", methods=["PUT"])
def cancel_order(order_id):
    """
    Cancel an Order
    This endpoint will cancel an order
    """
    app.logger.info("Action to cancel order with order_id: %s", order_id)
    order = Order.find_or_404(order_id)
    #data = request.get_json()
    #del data["order_items"]
    #order.deserialize(data)
    
    #order.id = order_id
    order.status = OrderStatus.Cancelled
    order.update()
    return make_response(
        jsonify(order.serialize()), status.HTTP_200_OK
    )

######################################################################
# DELETE AN ORDER
######################################################################
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
    return make_response("", status.HTTP_204_NO_CONTENT)
