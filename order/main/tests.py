from django.test import TestCase
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from .models import OrderCustomer, Order
from .status import Status

from .exceptions import OrderAlreadyCompletedError
from .exceptions import OrderCancellationError
from .exceptions import InvalidArgumentError

# Class to Setup data for our Tests
class OrderModelTestCase(TestCase):

  @classmethod
  def setUpTestData(cls):
    cls.customer_001 = OrderCustomer.objects.create(customer_id=1, email='customer001@mail.com')
    Order.objects.create(order_customer=cls.customer_001)
    Order.objects.create(order_customer=cls.customer_001, status=Status.Completed.value)

    cls.customer_002 = OrderCustomer.objects.create(customer_id=1, email='customer002@mail.com')
    Order.objects.create(order_customer=cls.customer_002)

  # Only cancel orders with status Recieved
  def test_cancel_order(self):
    order = Order.objects.get(pk=1)

    self.assertIsNotNone(order)
    self.assertEqual(Status.Received.value, order.status)

    Order.objects.cancel_order(order)
    self.assertEqual(Status.Cancelled.value, order.status)

  # Cannot cancle completed orders
  def test_cancel_completed_orders(self):
    order = Order.objects.get(pk=2)

    self.assertIsNotNone(order)
    self.assertEqual(Status.Completed.value, order.status)

    with self.assertRaises(OrderCancellationError):
      Order.object.cancel_order(order)

  # Cannot cancel with wrong parameter item (est if the correct exception is raised)
  def test_cancel_order_with_invalid_argument(self):
    with self.assertRaises(InvalidArgumentError):
      Order.objects.cancel_order({ 'id': 1 })

  # correct number of orders is returned when given a customer ID
  def test_get_all_orders_by_customer(self):
    orders = Order.objects.get_all_orders_by_customer(customer_id=1)

    self.assertEqual(2, len(orders), msg='Should have returned 2 orders')

  # correct exception is raised when passing an invalid argument
  def test_get_all_order_by_customer_with_invalid_id(self):
    with self.assertRaises(InvalidArgumentError):
      Order.objects.get_all_orders_by_customer('o')

  def test_get_customer_incomplete_orders(self):
    orders = Order.objects.get_customer_incomplete_orders(customer_id=1)

    self.assertEquals(1, len(orders))
    self.assertEquals(Status.Received.value, orders[0].status)
  
  def test_get_customer_incomplete_orders_with_invalid_id(self):
    with self.assertRaises(InvalidArgumentError):
      Order.objects.get_customer_incomplete_orders('o')
