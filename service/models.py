"""
This module contains the database models for order and order item resources.
"""

from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from service import APP

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DatabaseConnectionError(Exception):
    """Custom Exception when database connection fails"""


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """


DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'


class OrderStatus(Enum):
    """
        This enum defines the status values an order can exist in.
    """
    CREATED = 0
    PAID = 1
    COMPLETED = 2
    CANCELLED = 3


class PersistentBase():
    """ Base class added persistent methods """

    def __init__(self):
        self.id = None  # pylint: disable=invalid-name

    def create(self):
        """
        Creates an Order or Item to the database
        """
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates an Order or Item to the database
        """
        APP.logger.debug("Updating %s", self.id)
        db.session.commit()

    def delete(self):
        """ Removes an Order or Item from the database """
        APP.logger.debug("Deleting %s", self.id)
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        APP.logger.debug("Initializing database")
        cls.APP = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the records in the database """
        APP.logger.debug("Processing all records")
        return cls.query.all()  # pylint: disable=no-member

    @classmethod
    def find(cls, by_id):
        """ Finds a record by it's ID """
        APP.logger.debug("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)  # pylint: disable=no-member

    @classmethod
    def find_or_404(cls, by_id):
        """ Find a record by it's id """
        APP.logger.debug("Processing lookup or 404 for id %s ...", by_id)
        return cls.query.get_or_404(by_id)  # pylint: disable=no-member


class Item(db.Model, PersistentBase):
    """ Class that represents an Item """
    APP = None

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))

    def __init__(self, **kwargs):
        super().__init__()
        if "id" in kwargs:
            self.id = kwargs["id"]
        if "product_id" in kwargs:
            self.product_id = kwargs["product_id"]
        if "quantity" in kwargs:
            self.quantity = kwargs["quantity"]
        if "price" in kwargs:
            self.price = kwargs["price"]
        if "order_id" in kwargs:
            self.order_id = kwargs["order_id"]

    def __repr__(self):
        return f"Item('{self.id}', '{self.product_id}', '{self.quantity}', '{self.price}', '{self.order_id}')"    # pylint: disable=line-too-long

    def serialize(self):
        """ Serializes a Address into a dictionary """
        return {
            "id": self.id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "price": self.price,
            "order_id": self.order_id,
        }

    def deserialize(self, data: dict):
        """
        Deserializes a Item from a dictionary
        Args:
            data (dict): A dictionary containing the Item data
        """
        try:
            if "id" in data:
                self.id = data["id"]

            self.product_id = data["product_id"]
            self.quantity = data["quantity"]
            self.price = data["price"]

            if "order_id" in data:
                self.order_id = data["order_id"]

        except AttributeError as error:
            raise DataValidationError(
                "Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Item: missing " + error.args[0]) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Item: body of request contained bad or no data"
            ) from error
        return self


class Order(db.Model, PersistentBase):
    """
    This class contains the database schema for Order objects
    """
    APP = None
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    tracking_id = db.Column(db.Integer)
    status = db.Column(
        db.Enum(OrderStatus), nullable=False, server_default=(OrderStatus.CREATED.name)
    )
    items = db.relationship(
        'Item', backref='order', cascade="all, delete", lazy=True)

    def __init__(self, **kwargs):
        super().__init__()
        if "id" in kwargs:
            self.id = kwargs["id"]
        if "customer_id" in kwargs:
            self.customer_id = kwargs["customer_id"]
        if "tracking_id" in kwargs:
            self.tracking_id = kwargs["tracking_id"]
        if "status" in kwargs:
            self.status = kwargs["status"]
        if "items" in kwargs:
            self.items = kwargs["items"]

    def __repr__(self):
        return f"Order('{self.id}', '{self.customer_id}', '{self.tracking_id}', '{self.status}')"

    def serialize(self):
        """ Serializes a Address into a dictionary """
        items = []
        for item in self.items:
            items.append(Item.serialize(item))

        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "tracking_id": self.tracking_id,
            "status": self.status.name,
            "items": items,
        }

    def deserialize(self, data: dict):
        """
        Deserializes an Order from a dictionary
        Args:
            data (dict): A dictionary containing the Order data
        """
        try:
            if "id" in data:
                self.id = data["id"]

            self.customer_id = data["customer_id"]
            self.tracking_id = data["tracking_id"]

            if "items" in data:
                self.items = []
                for item in data["items"]:
                    self.items.append(
                        Item().deserialize(item))
            self.status = getattr(OrderStatus, data["status"])
        except AttributeError as error:
            raise DataValidationError(
                "Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Order: missing " + error.args[0]) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Order: body of request contained bad or no data") from error
        return self

    @classmethod
    def find_by_status(cls, status):
        """Returns all Orders with the given status

        Args:
            status (string): the status of the Order you want to match
        """
        APP.logger.debug("Processing status query for %s ...", status)
        return cls.query.filter(cls.status == status).all()

    @classmethod
    def find_by_customer(cls, customer_id):
        """Returns all Orders of the given customer ID

        Args:
            customer_id (int): the id of the Customer you want to match
        """
        APP.logger.debug("Processing customer query for %d ...", customer_id)
        return cls.query.filter(cls.customer_id == customer_id).all()
