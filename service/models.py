from enum import Enum
from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

class Order(db.Model):
    """
    Class that represents an Order
    """
    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer,)

    def __repr__(self):
        return "<Order %r id=[%s]>" % (self.order_id, self.id)

    def create(self):
        """
        Creates an Order in the database
        """
        self.id = None  # id must be none to generate next primary key
        self.order_id = 100
        db.session.add(self)
        db.session.commit()
    
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