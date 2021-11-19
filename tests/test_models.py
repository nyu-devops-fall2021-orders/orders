"""
Test cases for Order and OrderItem Models
"""
import logging
import unittest
import factories
import os
from service.models import Order, OrderItem, db, OrderStatus, DataValidationError
from datetime import datetime
from service.models import Order, OrderItem
from service import app

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)

######################################################################
#  O R D E R   I T E M   M O D E L   T E S T   C A S E S
######################################################################
class TestYourResourceModel(unittest.TestCase):
    """ Test Cases for YourResourceModel Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Order.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    # Order Tests
    def test_create_order(self):
        """ Create an order and assert that it exists """
        order_items = [OrderItem(product_id=1, quantity=1, price=5, order_id = 1)]
        order = Order(customer_id=123, order_items=order_items,status=OrderStatus.Created)
       
        self.assertTrue(order is not None)
        self.assertEqual(order.id, None)
        self.assertEqual(order.customer_id, 123)
        self.assertEqual(len(order.order_items), 1)
        self.assertEqual(order.status,OrderStatus.Created)
        self.assertEqual(order.tracking_id,None)
        
    def test_add_order(self):
        """Create an order and add it to the database"""
        order = Order.all()
        self.assertEqual(order, [])
        order = Order(customer_id=123, order_items=[],status=OrderStatus.Created, tracking_id= 1)
        self.assertTrue(order != None)
        self.assertEqual(order.id, None)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(order.id, 1)
        order = Order.all()
        self.assertEqual(len(order), 1)

    def test_update_order(self):
        """ Update an order """
        order = Order(customer_id=123, order_items=[],status=OrderStatus.Created, tracking_id= 1)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(order.id, 1)

        # Fetch it back
        order = Order.find(order.id)
        order.tracking_id = 2
        order.update()

        # Fetch it back again
        order = Order.find(order.id)
        self.assertEqual(order.tracking_id, 2)
    
    def test_delete_order(self):
        """ Delete an order from the database """
        order = Order.all()
        self.assertEqual(order, [])
        order = Order(customer_id=123, order_items=[],status=OrderStatus.Created, tracking_id= 1)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(order.id, 1)
        orders = Order.all()
        self.assertEqual(len(orders), 1)
        order = orders[0]
        order.delete()
        orders = Order.all()
        self.assertEqual(len(orders), 0)

    def test_find_or_404(self):
        """ Find or throw 404 error """
        order = Order(customer_id=123, order_items=[],status=OrderStatus.Created, tracking_id= 1)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(order.id, 1)

        # Fetch it back
        order = Order.find_or_404(order.id)
        self.assertEqual(order.id, 1)

    def test_serialize_order(self):
        """ Serialize an order """
        order_item = OrderItem(id=1, product_id=1, quantity=1, price=5, order_id = 1)
        order = Order(id=1, customer_id=123, order_items=[order_item],status=OrderStatus.Created, tracking_id= 1)
        serial_order = order.serialize()
        self.assertEqual(serial_order['id'], order.id)
        self.assertEqual(serial_order['customer_id'], order.customer_id)
        self.assertEqual(serial_order['status'], order.status.name)
        self.assertEqual(serial_order['tracking_id'], order.tracking_id)
        self.assertEqual(len(serial_order['order_items']), 1)
        order_items = serial_order['order_items']
        self.assertEqual(order_items[0]['id'], order_item.id)
        self.assertEqual(order_items[0]['product_id'], order_item.product_id)
        self.assertEqual(order_items[0]['quantity'], order_item.quantity)
        self.assertEqual(order_items[0]['price'], order_item.price)
        self.assertEqual(order_items[0]['order_id'], order_item.order_id)

    def test_deserialize_order(self):
        """ Deserialize an order """
        order_item = OrderItem(id=1, product_id=1, quantity=1, price=5, order_id = 1)
        order = Order(id=1, customer_id=123, order_items=[order_item],status=OrderStatus.Created, tracking_id= 1)
        serial_order = order.serialize()
        new_order = Order()
        new_order.deserialize(serial_order)
        self.assertEqual(new_order.id, order.id)
        self.assertEqual(new_order.customer_id, order.customer_id)
        self.assertEqual(new_order.status, order.status)
        self.assertEqual(new_order.tracking_id, order.tracking_id)
        new_order_items = new_order.order_items
        self.assertEqual(len(new_order_items), 1)
        self.assertEqual(new_order_items[0].id, order_item.id)
        self.assertEqual(new_order_items[0].product_id, order_item.product_id)
        self.assertEqual(new_order_items[0].quantity, order_item.quantity)
        self.assertEqual(new_order_items[0].price, order_item.price)
        self.assertEqual(new_order_items[0].order_id, order_item.order_id)

    def test_deserialize_with_key_error(self):
        """ Deserialize an order with a KeyError """
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, {})

    def test_deserialize_with_type_error(self):
        """ Deserialize an order with a TypeError """
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, [])
    
    def test_deserialize_order_item_key_error(self):
        """ Deserialize an order_item with a KeyError """
        order_item = OrderItem()
        self.assertRaises(DataValidationError, order_item.deserialize, {})

    def test_deserialize_order_item_type_error(self):
        """ Deserialize an order_item with a TypeError """
        order_item = OrderItem()
        self.assertRaises(DataValidationError, order_item.deserialize, [])

    # Order Items tests
    def test_add_order_with_items(self):
        """ Create an order with items and add it to the database """
        orders = Order.all()
        self.assertEqual(orders, [])
        order = Order(id=1, customer_id=123, order_items=[],status=OrderStatus.Created, tracking_id= 1)
        order_item = OrderItem(id=1, product_id=1, quantity=1, price=5, order_id = 1)
        order.order_items.append(order_item)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(order.id, 1)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

        new_order = Order.find(order.id)
        self.assertEqual(new_order.order_items[0].id, order_item.id)

        order_item2 = OrderItem(id=2, product_id=2, quantity=10, price=50, order_id = 1)
        order.order_items.append(order_item2)
        order.update()

        new_order = Order.find(order.id)
        self.assertEqual(len(new_order.order_items), 2)
        self.assertEqual(new_order.order_items[1].id, order_item2.id)

    def test_update_order_with_items(self):
        """ Update an order's items """
        orders = Order.all()
        self.assertEqual(orders, [])

        order_item = OrderItem(id=1, product_id=1, quantity=1, price=5, order_id = 1)
        order = Order(id=1, customer_id=123, order_items=[order_item],status=OrderStatus.Created, tracking_id= 1)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(order.id, 1)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

        # Fetch it back
        order = Order.find(order.id)
        old_order_item = order.order_items[0]
        self.assertEqual(old_order_item.product_id, order_item.product_id)

        old_order_item.product_id = 2
        order.update()

        # Fetch it back again
        order = Order.find(order.id)
        order_item = order.order_items[0]
        self.assertEqual(order_item.product_id, 2)

    def test_delete_account_address(self):
        """ Delete an order's order item """
        orders = Order.all()
        self.assertEqual(orders, [])

        order_item = OrderItem(id=1, product_id=1, quantity=1, price=5, order_id = 1)
        order = Order(id=1, customer_id=123, order_items=[order_item],status=OrderStatus.Created, tracking_id= 1)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(order.id, 1)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

        # Fetch it back
        order = Order.find(order.id)
        order_item = order.order_items[0]
        order_item.delete()
        order.update()

        # Fetch it back again
        order = Order.find(order.id)
        self.assertEqual(len(order.order_items), 0)

    def test_filter_orders_by_status(self):
        """ Get orders filtered by status """
        order = factories.OrderFactory(status=OrderStatus.Cancelled)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(order.id, 1)
        orders = Order.all()
        self.assertEqual(len(orders), 1)


        # Fetch filtered orders - different status
        orders = Order.find_by_status(OrderStatus.Completed)
        print('first', orders)
        self.assertEqual(len(orders), 0)
        
        # Fetch filtered orders - same status
        orders = Order.find_by_status(OrderStatus.Cancelled)
        print('second', orders)
        self.assertEqual(len(orders), 1)
        order = orders[0]
        self.assertEqual(order.id, 1)
        self.assertEqual(order.status, OrderStatus.Cancelled)
        
        