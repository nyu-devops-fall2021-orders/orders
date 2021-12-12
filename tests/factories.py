"""
Test Factory to make fake objects for testing
"""
import factory
from factory import fuzzy
from service.models import Order, Item, OrderStatus

# pylint: disable=too-few-public-methods,missing-class-docstring


class ItemFactory(factory.Factory):
    """ Creates fake Item """

    class Meta:
        model = Item

    id = factory.Sequence(lambda n: n)
    product_id = factory.Sequence(lambda n: n*100)
    quantity = factory.Sequence(lambda n: n*10)
    price = factory.Sequence(lambda n: n*45)

    def __init__(self, order_id=1):
        self.order_id = order_id


class OrderFactory(factory.Factory):
    """ Creates fake Orders """
    class Meta:
        model = Order

    id = factory.Sequence(lambda n: n)
    customer_id = factory.Sequence(lambda n: n*100)
    status = fuzzy.FuzzyChoice(OrderStatus)

    def __init__(self, status=None, customer_id=0):
        if status:
            self.status = status
        if customer_id > 0:
            self.customer_id = customer_id
