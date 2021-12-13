"""
This module contains all the API routes for orders.
"""
from flask_restx import Resource, fields, reqparse
from service.models import Order, OrderStatus
from service import APP, status
from service.routes.common import API, abort
from service.routes.items import item_create_model, item_model

# pylint: disable=no-self-use

order_core_model = API.model('OrderCore', {
    'customer_id': fields.Integer(required=True,
                                  description='The customer that placed the order'),
    'tracking_id': fields.Integer(required=True,
                                  description='The id used to track the shipment of the order'),
    'status': fields.String(enum=[s.name for s in OrderStatus],
                            description='The status that the order is currently in'),
})

order_create_model = API.inherit(
    'OrderCreate',
    order_core_model,
    {
        'items': fields.List(fields.Nested(item_create_model),
                             required=False,
                             description='The items that the order contains'),
    }
)

order_model = API.inherit(
    'Order',
    order_core_model,
    {
        'items': fields.List(fields.Nested(item_model),
                             required=False,
                             description='The items that the order contains'),
        'id': fields.Integer(readOnly=True,
                             description='The unique id assigned internally by service'),
    }
)

# query string arguments
order_args = reqparse.RequestParser()
order_args.add_argument('status', type=str, required=False,
                        help='List orders by status')
order_args.add_argument('customer-id', type=str,
                        required=False, help='List orders of a customer')

######################################################################
#  PATH: /orders/{id}
######################################################################


@API.route('/orders/<order_id>')
@API.param('order_id', 'The Order identifier')
class OrderResource(Resource):
    """
    OrderResource class

    Allows the manipulation of a single Order
    GET /orders/{id} - Returns an Order with the id
    PUT /orders/{id} - Update an Order with the id
    DELETE /orders/{id} -  Deletes an order with the id
    """

    # ------------------------------------------------------------------
    # FETCH ORDER
    # ------------------------------------------------------------------
    @API.doc('get_orders')
    @API.response(404, 'Order not found')
    @API.marshal_with(order_model)
    def get(self, order_id):
        """
        Retrieve a single Order
        This endpoint will return a order based on it's id
        """
        APP.logger.info("Request for order with id: %s", order_id)
        order = Order.find(order_id)
        if not order:
            abort(status.HTTP_404_NOT_FOUND,
                  f"Order with id '{order_id}' was not found.")
        return order.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE ORDER
    # ------------------------------------------------------------------
    @API.doc('update_orders')
    @API.response(404, 'Order not found')
    @API.response(400, 'The posted Order data was not valid')
    @API.expect(order_model)
    @API.marshal_with(order_model)
    def put(self, order_id):
        """
        Update an Order

        This endpoint will update an Order based the body that is posted
        """
        APP.logger.info("Request to update order with order_id: %s", order_id)
        order = Order.find(order_id)
        if not order:
            abort(status.HTTP_404_NOT_FOUND,
                  f"Order with id [{order_id}] was not found.")
        data = API.payload
        APP.logger.debug("Payload = %s", data)
        # Remove items because we do not want to update them through this endpoint
        if "items" in data:
            del data["items"]
        order.deserialize(data)

        order.id = order_id
        order.update()
        return order.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE ORDER
    # ------------------------------------------------------------------
    @API.doc('delete_orders')
    @API.response(204, 'Order deleted')
    def delete(self, order_id):
        """
        Delete an Order

        This endpoint will delete an Order based the id specified in the path
        """
        APP.logger.info("Request to delete order with id [%s]", order_id)
        order = Order.find(order_id)
        if order:
            order.delete()
            APP.logger.info('Order with id [%s] was deleted', order_id)
        return "", status.HTTP_204_NO_CONTENT

######################################################################
#  PATH: /orders
######################################################################


@API.route('/orders', strict_slashes=False)
class OrderCollection(Resource):
    """ Handles all interactions with collections of Orders """
    # ------------------------------------------------------------------
    # LIST ORDERS
    # ------------------------------------------------------------------
    @API.doc('list_orders')
    @API.expect(order_args, validate=True)
    @API.marshal_list_with(order_model)
    def get(self):
        """ Returns all of the Orders """
        APP.logger.info("Request to list orders...")
        APP.logger.info("Parsing args")
        if order_args:
            args = order_args.parse_args()
        APP.logger.info("Parsed args")
        if args is not None:
            if 'status' in args:
                order_status = args['status']
            if 'customer-id' in args:
                customer_id_str = args['customer-id']
        if order_status:
            APP.logger.info('Filtering by status: %s', order_status)
            orders = Order.find_by_status(OrderStatus[order_status])
        elif customer_id_str:
            APP.logger.info('Filtering by customer id: [%s]', customer_id_str)
            orders = Order.find_by_customer(int(customer_id_str))
        else:
            APP.logger.info('Returning unfiltered list')
            orders = Order.all()
        results = [order.serialize() for order in orders]
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # CREATE ORDER
    # ------------------------------------------------------------------
    @API.doc('create_orders')
    @API.response(400, 'The posted data was not valid')
    @API.expect(order_create_model)
    @API.marshal_with(order_model, code=201)
    def post(self):
        """
        Creates an Order

        This endpoint will create an Order based the data in the body that is posted
        """
        APP.logger.info("Request to create an order")

        order = Order()
        data = API.payload
        APP.logger.debug('Payload = %s', data)
        order.deserialize(data)
        order.create()
        # if 'items' in data:
        #     for item_data in data['items']:
        #         item = Item()
        #         item.deserialize(item_data)
        #         item.create()
        # order = Order.find(order.id)
        APP.logger.info('Order with new id [%s] created!', order.id)
        location_url = API.url_for(
            OrderResource, order_id=order.id, _external=True)
        return order.serialize(), status.HTTP_201_CREATED, {'Location': location_url}

######################################################################
#  PATH: /orders/{id}
######################################################################


@API.route('/orders/<order_id>/cancel')
@API.param('order_id', 'The Order identifier')
class OrderCancel(Resource):
    """ Cancel an Order """

    # ------------------------------------------------------------------
    # CREATE ORDER
    # ------------------------------------------------------------------
    @API.doc('cancel_orders')
    @API.response(404, 'Order not found')
    def put(self, order_id):
        """
        Cancel an Order

        This endpoint will cancel an order
        """
        APP.logger.info("Action to cancel order with order_id [%s]", order_id)
        order = Order.find(order_id)
        if not order:
            abort(status.HTTP_404_NOT_FOUND,
                  f"Order with id '{order_id}' was not found.")
        order.status = OrderStatus.CANCELLED
        order.update()
        return order.serialize(), status.HTTP_200_OK
