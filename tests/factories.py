"""
Test Factory to make fake objects for testing
"""
import factory
from datetime import datetime
from factory.fuzzy import FuzzyChoice
from service.models import Order, OrderItem, OrderStatus

class OrderItemFactory(factory.Factory):
    """ Creates fake OrderItem """

    class Meta:
        model = OrderItem

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
    status = factory.fuzzy.FuzzyChoice([s.value for s in OrderStatus])

    def __init__(self, items=0, status=None):
        if items > 0:
            order_items = OrderItemFactory.create_batch(items)
            self.order_items = order_items
        if status:
            self.status = status
        return 
