"""
Test cases for YourResourceModel Model
"""
import logging
import unittest
import os
from service.models import Order, OrderItem, db, OrderStatus
from datetime import datetime
from service.models import Order, OrderItem
from service import app

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)

######################################################################
#  <your resource name>   M O D E L   T E S T   C A S E S
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

    def test_model_order(self):
        """ Test something """
        self.assertTrue(True)
        order_items = [OrderItem(id=1, product_id=1, quantity=1, price=5, order_id = 1)]
        
        order_item = order_items[0]
        self.assertTrue(order_item is not None)
        self.assertEqual(order_item.product_id,1)
        self.assertEqual(order_item.quantity,1)
        self.assertEqual(order_item.price,5)
        self.assertEqual(order_item.order_id,1)
        self.assertEqual(order_item.id,1)

        order = Order(customer_id=123, order_items=order_items,status=OrderStatus.Created)
       
        self.assertTrue(order is not None)
        self.assertEqual(order.id, None)
        self.assertEqual(order.customer_id, 123)
        self.assertEqual(len(order.order_items), 1)
        self.assertEqual(order.status,OrderStatus.Created)
        self.assertEqual(order.tracking_id,None)
        
        

