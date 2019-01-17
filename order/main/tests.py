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

  def test_get_customer_completed_orders(self):
    orders = Order.objects.get_customer_completed_orders(customer_id=1)

    self.assertEqual(1, len(orders))
    self.assertEqual(Status.Completed.value, orders[0].status)
  
  def test_get_customer_completed_orders_with_invalid_id(self):
    with self.assertRaises(InvalidArgumentError):
      Order.objects.get_customer_completed_orders('0')

  def test_get_order_by_status(self):
    order = Order.objects.get_order_by_status(Status.Received)

    self.assertEqual(2, len(order), msg=('There should be only 2 orders with status=Received.'))
    self.assertEqual('customer_001@test.com', order[0].order_customer.email)

  def test_get_order_by_status_with_invalid_status(self):
    with self.assertRaises(InvalidArgumentError):
      Order.objects.get_order_by_status(1)

  ## Test Fetch orders by given date range period
  ### When valid periods are passed
  def test_get_orders_by_period(self):
    date_from = timezone.now() - relativedelta(days=1) # Current date Minus one day
    date_to = date_from + relativedelta(days=2)

    orders = Order.objects.get_orders_by_period(date_from, date_to)
    self.assertEqual(3, len(orders))

    date_from = timezone.now() + relativedelta(days=3)
    date_to = date_from + relativedelta(months=1)

    orders = Order.objects.get_orders_by_period(date_from, date_to)
    self.assertEqual(0, len(orders))

  def test_get_orders_by_period_with_invalid_start_date(self):
    start_date = timezone.now()

    with self.assertRaises(InvalidArgumentError):
      Order.objects.get_orders_by_period(start_date, None)

  def test_get_orders_by_period_with_invalid_end_date(self):
    end_date = timezone.now()

    with self.assertRaises(InvalidArgumentError):
      Order.objects.get_orders_by_period(None, end_date)

  ### Setting the order's next status
  def test_set_next_status(self):
    order = Order.objects.get(pk=1)
    self.assertTrue(order is not None, msg='The order is None.')
    self.assertEqual(Status.Received.value, order.status, msg='The status should have been Status.Received.')

    Order.objects.set_next_status(order)
    self.assertEqual(Status.Processing.value, order.status, msg='The status should have been Status.Processing.')

  def test_set_next_status_on_completed_order(self):
    order = Order.objects.get(pk=2)

    with self.assertRaises(OrderAlreadyCompletedError):
      Order.objects.set_next_status(order)

  def test_set_next_status_on_invalid_order(self):
    with self.assertRaises(InvalidArgumentError):
      Order.objects.set_next_status({'order': 1})

  ### Test for set_status() Method 
  def test_set_next_status(self):
    order = Order.objects.get(pk=1)

    self.assertTrue(order is not None, msg='The order is None.')

    self.assertEqual(Status.Received.value, order.status, msg='The status should have been Status.Received.')

    Order.objects.set_next_status(order)

    self.assertEqual(Status.Processing.value, order.status, msg='The status should have been Status.Processing.')

  # Cannot set status on completed Order
  def test_set_next_status_on_completed_order(self):
    order = Order.objects.get(pk=2)

    with self.assertRaises(OrderAlreadyCompletedError):
      Order.objects.set_next_status(order)

  # Cannot set status on invalid order
  def test_set_next_status_on_invalid_order(self):
    with self.assertRaises(InvalidArgumentError):
      Order.objects.set_next_status({'order': 1})

  def test_set_status(self):
    order = Order.objects.get(pk=1)

    Order.objects.set_status(order, Status.Processing)
      self.assertEqual(Status.Processing.value, order.status)

  def test_set_status_on_completed_order(self):
    order = Order.objects.get(pk=2)

    with self.assertRaises(OrderAlreadyCompletedError):
      Order.objects.set_status(order, Status.Processing)

  def test_set_status_on_cancelled_order(self):
    order = Order.objects.get(pk=1)
    Order.objects.cancel_order(order)

    with self.assertRaises(OrderAlreadyCancelledError):
      Order.objects.set_status(order, Status.Processing)

  def test_set_status_with_invalid_order(self):
    with self.assertRaises(InvalidArgumentError):
      Order.objects.set_status(None, Status.Processing)

  def test_set_status_with_invalid_status(self):
    order = Order.objects.get(pk=1)

    with self.assertRaises(InvalidArgumentError):
      Order.objects.set_status(order, {'status': 1})