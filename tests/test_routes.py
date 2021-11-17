"""
TestYourResourceModel API Service Test Suite
Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
#from service import status  # HTTP Status Codes
from service.models import db, Order, OrderItem, OrderStatus
from service.routes import app, init_db
from service import status
from tests.factories import OrderFactory, OrderItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)

######################################################################
#  T E S T   C A S E S
######################################################################
class TestYourResourceServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db()

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()

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
        orderStatus = OrderStatus.Created
        tracking_id = 1
        for _ in range(count):
            order = Order(customer_id=customer_id, tracking_id=tracking_id, status=orderStatus)
            resp = self.app.post(
                "/order", json=order.serialize(), content_type="application/json"
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test Account"
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
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_order_list(self):
        """ Get a list of orders """
        self._create_orders(5)
        resp = self.app.get("/order")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_order(self):
        """ Get a single Order """
        # get the id of an order
        order = self._create_orders(1)[0]
        order.create()
        resp = self.app.get(
            "/order/{}".format(order.id), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["customer_id"], order.customer_id)

    def test_get_order_not_found(self):
        """ Get an order that is not found """
        resp = self.app.get("/order/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_order(self):
        """ Create a new Account """
        order_item = OrderItem(product_id=1, quantity=1, price=5, order_id = 1)
        order = Order(customer_id=1, tracking_id=1, status=OrderStatus.Created, order_items=[order_item])
        resp = self.app.post(
            "/order", 
            json=order.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        
        # Check the data is correct
        new_order = resp.get_json()
        self.assertNotEqual(new_order["id"], None, "Order ID is null")
        self.assertEqual(new_order["customer_id"], order.customer_id, "Customer ID does not match")
        self.assertEqual(new_order["tracking_id"], order.tracking_id, "Tracking ID does not match")
        self.assertEqual(new_order["status"], order.status.name, "Status does not match")
        self.assertEqual(len(new_order["order_items"]), 1, "Order items has length not equal to 1")

        new_order_item = new_order["order_items"][0]
        # Check that the location header was correct by getting it
        resp = self.app.get(
            "/order/{}/orderitem/{}".format(new_order["id"], new_order_item["id"]),
            json=order.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_order_item = resp.get_json()
        self.assertEqual(new_order_item["product_id"], order_item.product_id, "Product ID does not match")
        self.assertEqual(new_order_item["quantity"], order_item.quantity, "Quantity does not match")
        self.assertEqual(new_order_item["price"], order_item.price, "Price does not match")
        self.assertEqual(new_order_item["order_id"], order_item.order_id, "Order ID does not match")

    def test_update_order(self):
        """ Update an existing order """
        # create an Account to update
        order_item = OrderItem(product_id=1, quantity=1, price=5, order_id = 1)
        order = Order(customer_id=1, tracking_id=1, status=OrderStatus.Created, order_items=[order_item])
        resp = self.app.post(
            "/order", 
            json=order.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the order
        new_order = resp.get_json()
        new_order["customer_id"] = 456
        resp = self.app.put(
            "/order/{}".format(new_order["id"]),
            json=new_order,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_order = resp.get_json()
        self.assertEqual(updated_order["customer_id"], 456)

    def test_delete_order(self):
        """ Delete an Account """
        # get the id of an order
        order = self._create_orders(1)[0]
        resp = self.app.delete(
            "/order/{}".format(order.id), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_action_status(self):
        """ change the status of an order to cancelled """
        # create an Action to change order status to canceled
        order_item = OrderItem(product_id=1, quantity=1, price=5, order_id = 1)
        order = Order(customer_id=1, tracking_id=1, status=OrderStatus.Created, order_items=[order_item])
        resp = self.app.post(
            "/order", 
            json=order.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Action to cancel the order
        #new_order = resp.get_json()
        #new_order["status"] = OrderStatus.Cancelled
        resp = self.app.put(
            "/order/1/cancel"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_order = resp.get_json()
        self.assertEqual(updated_order["status"], OrderStatus.Cancelled.name)


    # Order Items

    def test_get_order_item_list(self):
        """ Get a list of order items """
        # add two order_itemes to account
        order = self._create_orders(1)[0]
        order_item_list = OrderItemFactory.create_batch(2)

        # Create order_item 1
        resp = self.app.post(
            "/order/{}/orderitem".format(order.id), 
            json=order_item_list[0].serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Create order_item 2
        resp = self.app.post(
            "/order/{}/orderitem".format(order.id), 
            json=order_item_list[1].serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # get the list back and make sure there are 2
        resp = self.app.get(
            "/order/{}/orderitem".format(order.id), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 2)


    def test_add_order_item(self):
        """ Add an item to an order """
        order = self._create_orders(1)[0]
        order_item = OrderItemFactory()
        resp = self.app.post(
            "/order/{}/orderitem".format(order.id), 
            json=order_item.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["order_id"], order.id)
        self.assertEqual(data["product_id"], order_item.product_id)
        self.assertEqual(data["quantity"], order_item.quantity)
        self.assertEqual(data["price"], order_item.price)

    def test_get_order_item(self):
        """ Get an order item from an order """
        # create a known order item
        order = self._create_orders(1)[0]
        order_item = OrderItemFactory()
        resp = self.app.post(
            "/order/{}/orderitem".format(order.id), 
            json=order_item.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        order_item_id = data["id"]

        # retrieve it back
        resp = self.app.get(
            "/order/{}/orderitem/{}".format(order.id, order_item_id), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["order_id"], order.id)
        self.assertEqual(data["product_id"], order_item.product_id)
        self.assertEqual(data["quantity"], order_item.quantity)
        self.assertEqual(data["price"], order_item.price)

    def test_update_order_item(self):
        """ Update an order_item on an account """
        # create a known order_item
        order = self._create_orders(1)[0]
        order_item = OrderItemFactory()
        resp = self.app.post(
            "/order/{}/orderitem".format(order.id), 
            json=order_item.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        order_item_id = data["id"]
        data["product_id"] = 123

        # send the update back
        resp = self.app.put(
            "/order/{}/orderitem/{}".format(order.id, order_item_id), 
            json=data, 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # retrieve it back
        resp = self.app.get(
            "/order/{}/orderitem/{}".format(order.id, order_item_id), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["id"], order_item_id)
        self.assertEqual(data["order_id"], order.id)
        self.assertEqual(data["product_id"], 123)

    def test_delete_order_item(self):
        """ Delete an order item """
        order = self._create_orders(1)[0]
        order_item = OrderItemFactory()
        resp = self.app.post(
            "/order/{}/orderitem".format(order.id), 
            json=order_item.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)
        order_item_id = data["id"]

        # send delete request
        resp = self.app.delete(
            "/order/{}/orderitem/{}".format(order.id, order_item_id),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # retrieve it back and make sure order_item is not there
        resp = self.app.get(
            "/order/{}/orderitem/{}".format(order.id, order_item_id), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)