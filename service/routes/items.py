"""
This module contains all the API routes for orders.
"""
from flask_restx import Resource, fields
from service.models import Order, Item
from service import APP, status
from service.routes.common import API, abort

# pylint: disable=no-self-use

item_create_model = API.model('ItemCreate', {
    'product_id': fields.Integer(required=True,
                                 description='The product that was purchased'),
    'quantity': fields.Integer(required=True,
                               description='The quantity of the product purchased'),
    'price': fields.Float(required=True,
                          description='The price at which the product was purchased'),
})

item_model = API.inherit(
    'Item',
    item_create_model,
    {
        'order_id': fields.Integer(required=True,
                                   description='The order in which the product was purchased'),
        'id': fields.Integer(readOnly=True,
                             description='The unique id assigned internally by service'),
    },
)


######################################################################
#  PATH: /orders/{order_id}/items/{item_id}
######################################################################

@API.route('/orders/<order_id>/items/<item_id>')
@API.param('order_id', 'The Order identifier')
@API.param('item_id', 'The Item identifier')
class ItemResource(Resource):
    """
    ItemResource class

    Allows the manipulation of a single Item
    GET /orders/{order_id}/items/{item_id} - Returns an Item with the id
    PUT /orders/{order_id}/items/{item_id} - Update an Item with the id
    DELETE /orders/{order_id}/items/{item_id} -  Deletes an Item with the id
    """

    # ------------------------------------------------------------------
    # FETCH ITEM
    # ------------------------------------------------------------------
    @API.doc('get_items')
    @API.response(404, 'Item not found')
    @API.marshal_with(item_model)
    def get(self, order_id, item_id):
        """
        Retrieve a single Item

        This endpoint will return an Item based on its id
        """
        APP.logger.info("Request for item with id [%s]", item_id)
        order = Order.find(order_id)
        if not order:
            abort(status.HTTP_404_NOT_FOUND,
                  f"Order with id '{order_id}' was not found.")
        item = Item.find(item_id)
        if not item:
            abort(status.HTTP_404_NOT_FOUND,
                  f"Item with id '{item_id}' was not found.")
        return item.serialize()

    # ------------------------------------------------------------------
    # UPDATE ITEM
    # ------------------------------------------------------------------
    @API.doc('update_items')
    @API.response(404, 'Item not found')
    @API.response(400, 'The posted Item data was not valid')
    @API.expect(item_model)
    @API.marshal_with(item_model)
    def put(self, order_id, item_id):
        """
        Update an Item

        This endpoint will update an Item based the body that is posted
        """
        APP.logger.info(
            "Request to update item with order_id [%s] and item_id [%s]", order_id, item_id)
        order = Order.find(order_id)
        if not order:
            abort(status.HTTP_404_NOT_FOUND,
                  f"Order with id '{order_id}' was not found.")
        item = Item.find(item_id)
        if not item:
            abort(status.HTTP_404_NOT_FOUND,
                  f"Item with id '{item_id}' was not found.")
        data = API.payload
        APP.logger.debug("Payload = %s", data)
        item.deserialize(data)
        item.id = item_id
        item.order_id = order_id
        item.update()
        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE ITEM
    # ------------------------------------------------------------------
    @API.doc('delete_items')
    @API.response(204, 'Item deleted')
    def delete(self, order_id, item_id):
        """
        Delete an Item

        This endpoint will delete an item based on its id
        """
        APP.logger.info(
            "Request to delete item with order_id [%s] and item_id [%s]", order_id, item_id)

        order = Order.find(order_id)
        if not order:
            abort(status.HTTP_404_NOT_FOUND,
                  f"Order with id '{order_id}' was not found.")
        item = Item.find(item_id)
        if item:
            item.delete()
        return "", status.HTTP_204_NO_CONTENT

######################################################################
#  PATH: /orders/{order_id}/items
######################################################################


@API.route('/orders/<order_id>/items', strict_slashes=False)
class ItemOrderCollection(Resource):
    """ Handles interactions with collections of Items for an Order """
    # ------------------------------------------------------------------
    # LIST ITEMS FOR ORDER
    # ------------------------------------------------------------------
    @API.doc('list_items_for_order')
    @API.marshal_list_with(item_model)
    def get(self, order_id):
        """ Returns all of the Items for an Order """

        APP.logger.info("Request to list items for order id [%s]", order_id)
        order = Order.find(order_id)
        if not order:
            abort(status.HTTP_404_NOT_FOUND,
                  f"Order with id '{order_id}' was not found.")
        results = [item.serialize() for item in order.items]
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # CREATE ITEM
    # ------------------------------------------------------------------
    @API.doc('create_items')
    @API.response(400, 'The posted data was not valid')
    @API.expect(item_create_model)
    @API.marshal_with(item_model, code=201)
    def post(self, order_id):
        """
        Creates an Item associated with an Order

        """
        APP.logger.info("Request to create an item")
        order = Order.find(order_id)
        APP.logger.info(str(order))
        if not order:
            abort(status.HTTP_404_NOT_FOUND,
                  f"Order with id '{order_id}' was not found.")

        data = API.payload
        APP.logger.debug("Payload = %s", data)
        item = Item()
        item.deserialize(data)
        # Make sure order_id does not change
        item.order_id = order_id
        item.create()

        # Add the item to the order
        # order.items.append(item)
        # order.update()
        return item.serialize(), status.HTTP_201_CREATED

######################################################################
#  PATH: /items
######################################################################


@API.route('/items', strict_slashes=False)
class ItemCollection(Resource):
    """ Handles interactions with collections of Items """

    # ------------------------------------------------------------------
    # LIST ALL ITEMS
    # ------------------------------------------------------------------
    @API.doc('list_items')
    @API.marshal_list_with(item_model)
    def get(self):
        """
        Lists all Items

        """
        all_items = Item.all()
        results = [Item.serialize(item) for item in all_items]

        return results, status.HTTP_200_OK
