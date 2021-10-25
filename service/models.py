from enum import Enum
import logging
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()
logger = logging.getLogger("flask.app")

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

    pass

DATETIME_FORMAT='%Y-%m-%d %H:%M:%S.%f'

class OrderStatus(Enum):
    Created = 0
    Paid = 1
    Completed = 2
    Cancelled = 3

class PersistentBase():
    """ Base class added persistent methods """

    def create(self):
        """
        Creates a Account to the database
        """
        logger.info("Creating %s", self.id)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def save(self):
        """
        Updates a Account to the database
        """
        logger.info("Saving %s", self.id)
        db.session.commit()

    def delete(self):
        """ Removes a Account from the data store """
        logger.info("Deleting %s", self.id)
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the records in the database """
        logger.info("Processing all records")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a record by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_or_404(cls, by_id):
        """ Find a record by it's id """
        logger.info("Processing lookup or 404 for id %s ...", by_id)
        return cls.query.get_or_404(by_id)

class OrderItem(db.Model, PersistentBase):
    """ Class that represents an Order Item """
    app = None

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    

    def __repr__(self):
        return f"Order Item('{self.id}', '{self.product_id}', '{self.quantity}', '{self.price}', '{self.order_id}')"
        #return "<OrderItem %r>" % self.item_id

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
        Deserializes a Order Item from a dictionary
        Args:
            data (dict): A dictionary containing the Order Item data
        """
        try:
            #self.id = data["id"]
            self.product_id = data["product_id"]
            self.quantity = data["quantity"]
            self.price = data["price"]
            #self.order_id = data["order_id"]
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0])
        except KeyError as error:
            raise DataValidationError("Invalid Order Item: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid Order Item: body of request contained bad or no data"
            )
        return self


class Order(db.Model, PersistentBase):
    """
    Class that represents an Order
    """
    # Table Schema
    app = None
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.now)
    updated_at = db.Column(db.DateTime(), default=datetime.now)
    tracking_id = db.Column(db.Integer)
    status = db.Column(
        db.Enum(OrderStatus), nullable=False, server_default=(OrderStatus.Created.name)
    )
    order_items = db.relationship('OrderItem', backref='order', cascade="all, delete", lazy=True)

    def __repr__(self):
        #return "<Order %r>" % self.id
        return f"Order('{self.id}', '{self.customer_id}', '{self.created_at}', '{self.tracking_id}')"



    '''id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer,)

    def __repr__(self):
        return "<Order %r id=[%s]>" % (self.order_id, self.id)'''

    def serialize(self):
        """ Serializes a Address into a dictionary """
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "tracking_id": self.tracking_id,
            "status": self.status.name,
        }
    
    def deserialize(self, data: dict):
        """
        Deserializes a Order from a dictionary
        Args:
            data (dict): A dictionary containing the Order data
        """
        try:
            #self.id = data["id"]
            self.customer_id = data["customer_id"]
            # The values given to created_at and updated_at by JSON are strings.
            # They get updated to  Datetime variables automatically when create() used.
            self.created_at = data["created_at"]
            self.updated_at = data["updated_at"]
            self.tracking_id = data["tracking_id"]
            #self.order_items = data["order_items"]
            self.status = getattr(OrderStatus, data["status"])
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0])
        except KeyError as error:
            raise DataValidationError("Invalid Order: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid Order: body of request contained bad or no data"
            )
        return self



