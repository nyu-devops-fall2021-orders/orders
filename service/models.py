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

class OrderStatus(Enum):
    Created = 0
    Paid = 1
    Completed = 2
    Cancelled = 3

class OrderItem(db.Model):
    """ Class that represents an Order Item """
    app = None

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    

    def __repr__(self):
        return "<OrderItem %r>" % self.item_id

    def deserialize(self, data: dict):
        """
        Deserializes a Order Item from a dictionary
        Args:
            data (dict): A dictionary containing the Order Item data
        """
        try:
            self.id = data["id"]
            self.product_id = data["product_id"]
            self.quantity = data["quantity"]
            self.price = data["price"]
            self.order_id = data["order_id"]
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0])
        except KeyError as error:
            raise DataValidationError("Invalid Order Item: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid Order Item: body of request contained bad or no data"
            )
        return self

    def create(self):
        """
        Creates a Pet to the database
        """
        logger.info("Creating %s", self.id)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()
    
    def all(cls):
        """ Returns all of the Pets in the database """
        return cls.query.all()

    


class Order(db.Model):
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
        return "<Order %r>" % self.id
        # return f"User('{self.username}', '{self.email}', '{self.image_file}')"



    '''id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer,)

    def __repr__(self):
        return "<Order %r id=[%s]>" % (self.order_id, self.id)'''

    def create(self):
        """
        Creates an Order in the database
        """
        self.id = None  # id must be none to generate next primary key
        #self.order_id = 100
        db.session.add(self)
        db.session.commit()
    
    def deserialize(self, data: dict):
        """
        Deserializes a Pet from a dictionary
        Args:
            data (dict): A dictionary containing the Pet data
        """
        try:
            self.id = data["id"]
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
            raise DataValidationError("Invalid pet: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid pet: body of request contained bad or no data"
            )
        return self
    
    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Pets in the database """
        return cls.query.all()
