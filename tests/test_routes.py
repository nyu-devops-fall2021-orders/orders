"""
Orders API Service Test Suite
Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from urllib.parse import quote_plus
from unittest import TestCase
from factories import ItemFactory
from service.models import DatabaseConnectionError, db, Order, Item, OrderStatus
from service.routes.common import init_db, request_validation_error, database_connection_error
from service import APP, status

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/api/orders"
LIST_ITEMS_URL = "/api/items"

######################################################################
#  T E S T   C A S E S
######################################################################


class TestYourResourceServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        APP.config['TESTING'] = True
        APP.config['DEBUG'] = False
        APP.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        APP.logger.setLevel(logging.CRITICAL)
        init_db()

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.APP = APP.test_client()    # pylint: disable=invalid-name

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_orders(self, count):
        """ Helper method to create orders in bulk """
        orders = []

        customer_id = 1
        order_status = OrderStatus.CREATED
        tracking_id = 1
        for _ in range(count):
            order = Order(customer_id=customer_id,
                          tracking_id=tracking_id, status=order_status)
            resp = self.APP.post(
                BASE_URL, json=order.serialize(), content_type="application/json"
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test Order"
            )
            new_order = resp.get_json()
            order.id = new_order["id"]
            orders.append(order)
            customer_id = customer_id + 1
            tracking_id = tracking_id + 1
        return orders

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ Test index call """
        resp = self.APP.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_order_list(self):
        """ Get a list of orders """
        self._create_orders(5)
        resp = self.APP.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_order(self):
        """ Get a single Order """
        # get the id of an order
        order = self._create_orders(1)[0]
        order.create()
        resp = self.APP.get(
            f"{BASE_URL}/{order.id}",
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["customer_id"], order.customer_id)

    def test_get_order_not_found(self):
        """ Get an order that is not found """
        resp = self.APP.get("{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_order(self):
        """ Create a new Order """
        item = Item(product_id=1, quantity=1, price=5, order_id=1)
        order = Order(customer_id=1, tracking_id=1,
                      status=OrderStatus.CREATED, items=[item])
        resp = self.APP.post(
            BASE_URL,
            json=order.serialize(),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Check the data is correct
        new_order = resp.get_json()
        self.assertNotEqual(new_order["id"], None, "Order ID is null")
        self.assertEqual(new_order["customer_id"],
                         order.customer_id, "Customer ID does not match")
        self.assertEqual(new_order["tracking_id"],
                         order.tracking_id, "Tracking ID does not match")
        self.assertEqual(new_order["status"],
                         order.status.name, "Status does not match")
        self.assertEqual(
            len(new_order["items"]), 1, "Order items has length not equal to 1")

        new_item = new_order["items"][0]
        # Check that the location header was correct by getting it
        resp = self.APP.get(
            f"{BASE_URL}/{new_order['id']}/items/{new_item['id']}",
            json=order.serialize(),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_item = resp.get_json()
        self.assertEqual(
            new_item["product_id"], item.product_id, "Product ID does not match")
        self.assertEqual(
            new_item["quantity"], item.quantity, "Quantity does not match")
        self.assertEqual(new_item["price"],
                         item.price, "Price does not match")
        self.assertEqual(
            new_item["order_id"], item.order_id, "Order ID does not match")

    def test_update_order(self):
        """ Update an existing order """
        # create an Order to update
        item = Item(product_id=1, quantity=1, price=5, order_id=1)
        order = Order(customer_id=1, tracking_id=1,
                      status=OrderStatus.CREATED, items=[item])
        resp = self.APP.post(
            BASE_URL,
            json=order.serialize(),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the order
        new_order = resp.get_json()
        new_order["customer_id"] = 456
        resp = self.APP.put(
            f"{BASE_URL}/{new_order['id']}",
            json=new_order,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_order = resp.get_json()
        self.assertEqual(updated_order["customer_id"], 456)

    def test_delete_order(self):
        """ Delete an Order """
        # get the id of an order
        order = self._create_orders(1)[0]
        resp = self.APP.delete(
            f"{BASE_URL}/{order.id}",
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_action_status(self):
        """ Cancel an Order """
        # create an Action to change order status to canceled
        order = self._create_orders(1)[0]
        order.create()
        self.assertEqual(order.status, OrderStatus.CREATED)

        # Action to cancel the order
        resp = self.APP.put(
            f"{BASE_URL}/{order.id}/cancel"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_order = resp.get_json()
        self.assertEqual(updated_order["status"], OrderStatus.CANCELLED.name)

        # Get order
        resp = self.APP.get(
            f"{BASE_URL}/{order.id}",
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["status"], OrderStatus.CANCELLED.name)

    # Items

    def test_get_item_list(self):
        """ Get a list of items """
        # add two items to single order
        order = self._create_orders(1)[0]
        item_list = ItemFactory.create_batch(2)

        # Create item 1
        resp = self.APP.post(
            f"{BASE_URL}/{order.id}/items",
            json=item_list[0].serialize(),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Create item 2
        resp = self.APP.post(
            f"{BASE_URL}/{order.id}/items",
            json=item_list[1].serialize(),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # get the list back and make sure there are 2
        resp = self.APP.get(
            f"{BASE_URL}/{order.id}/items",
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 2)

    def test_add_item(self):
        """ Add an item to an order """
        order = self._create_orders(1)[0]
        item = ItemFactory()
        resp = self.APP.post(
            f"{BASE_URL}/{order.id}/items",
            json=item.serialize(),  # pylint: disable=no-member
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        self.assertEqual(data["order_id"], order.id)
        self.assertEqual(data["product_id"], item.product_id)
        self.assertEqual(data["quantity"], item.quantity)
        self.assertEqual(data["price"], item.price)

    def test_get_item(self):
        """ Get an item from an order """
        # create a known item
        order = self._create_orders(1)[0]
        item = ItemFactory()
        resp = self.APP.post(
            f"{BASE_URL}/{order.id}/items",
            json=item.serialize(),  # pylint: disable=no-member
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        item_id = data["id"]

        # retrieve it back
        resp = self.APP.get(
            f"{BASE_URL}/{order.id}/items/{item_id}",
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(data["order_id"], order.id)
        self.assertEqual(data["product_id"], item.product_id)
        self.assertEqual(data["quantity"], item.quantity)
        self.assertEqual(data["price"], item.price)

    def test_update_item(self):
        """ Update an item """
        # create a known item
        order = self._create_orders(1)[0]
        item = ItemFactory()
        resp = self.APP.post(
            f"{BASE_URL}/{order.id}/items",
            json=item.serialize(),  # pylint: disable=no-member
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        item_id = data["id"]
        data["product_id"] = 123

        # send the update back
        resp = self.APP.put(
            f"{BASE_URL}/{order.id}/items/{item_id}",
            json=data,
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # retrieve it back
        resp = self.APP.get(
            f"{BASE_URL}/{order.id}/items/{item_id}",
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(data["id"], item_id)
        self.assertEqual(data["order_id"], order.id)
        self.assertEqual(data["product_id"], 123)

    def test_delete_item(self):
        """ Delete an item """
        order = self._create_orders(1)[0]
        item = ItemFactory()
        resp = self.APP.post(
            f"{BASE_URL}/{order.id}/items",
            json=item.serialize(),  # pylint: disable=no-member
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        item_id = data["id"]

        # send delete request
        resp = self.APP.delete(
            f"{BASE_URL}/{order.id}/items/{item_id}",
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # retrieve it back and make sure item is not there
        resp = self.APP.get(
            f"{BASE_URL}/{order.id}/items/{item_id}",
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_order_list_by_status(self):
        """ Query Orders by Status """
        orders = self._create_orders(10)
        test_status = orders[0].status
        status_orders = [
            order for order in orders if order.status == test_status]
        resp = self.APP.get(
            BASE_URL, query_string=f"status={quote_plus(test_status.name)}"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(status_orders))
        # check the data just to be sure
        for order in data:
            self.assertEqual(order["status"], test_status.name)

    def test_query_order_list_by_customer(self):
        """ Query Orders by Customer """
        orders = self._create_orders(10)
        test_customer_id = orders[0].customer_id
        customer_id_orders = [
            order for order in orders if order.customer_id == test_customer_id]
        resp = self.APP.get(
            BASE_URL, query_string=f"customer-id={test_customer_id}"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(customer_id_orders))
        # check the data just to be sure
        for order in data:
            self.assertEqual(order["customer_id"], test_customer_id)

    def test_request_validation_error(self):
        """ Check the body of request validation error """
        try:
            raise ValueError
        except ValueError as error:
            error_response, status_code = request_validation_error(error)
            self.assertEqual(status_code,
                             status.HTTP_400_BAD_REQUEST)
            self.assertEqual(error_response['error'],
                             'Bad Request')

    def test_database_validation_error(self):
        """ Check the body of database connection error """
        try:
            raise DatabaseConnectionError
        except DatabaseConnectionError as error:
            error_response, status_code = database_connection_error(error)
            self.assertEqual(status_code,
                             status.HTTP_503_SERVICE_UNAVAILABLE)
            self.assertEqual(error_response['error'],
                             'Service Unavailable')

    def test_get_nonexistent_order(self):
        """ Check fetch nonexistent order """
        order_id = 1
        resp = self.APP.get(
            f"{BASE_URL}/{order_id}",
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_item_nonexistent_order(self):
        """ Check fetch item from nonexistent order """
        order_id = 1
        item_id = 1
        resp = self.APP.get(
            f"{BASE_URL}/{order_id}/items/{item_id}",
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_nonexistent_item(self):
        """ Check fetch nonexistent item """
        self._create_orders(1)
        order_id = 1
        resp = self.APP.get(
            f"{BASE_URL}/{order_id}",
            content_type="application/json"
        )
        order = Order()
        order.deserialize(resp.get_json())
        self.assertEqual(order.id, 1)

        item_id = 1
        resp = self.APP.get(
            f"{BASE_URL}/{order_id}/items/{item_id}",
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_all_item_list(self):
        """ Get a list of all items """
        # add one item each to two orders
        [order_1, order_2] = self._create_orders(2)
        item_list = ItemFactory.create_batch(2)

        # Create item 1
        resp = self.APP.post(
            f"{BASE_URL}/{order_1.id}/items",
            json=item_list[0].serialize(),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Create item 2
        resp = self.APP.post(
            f"{BASE_URL}/{order_2.id}/items",
            json=item_list[1].serialize(),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # get the list back and make sure there are 2
        resp = self.APP.get(
            LIST_ITEMS_URL,
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 2)
