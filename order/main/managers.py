from datetime import datetime
from django.db.models import Q, Manager

from .models import models
from .status import Status
from .exceptions import InvalidArgumentError
from .exceptions import OrderAlreadyCompletedError
from .exceptions import OrderCancellationError

class OrderManager(Manager):

  # order is instance of Order and status is Item of Enum class Status
  def set_status(self, order, status):
    if status is None or not isinstance(status, Status):
      raise InvalidArgumentError('status')

    if order is None or not isinstance(order, models.Order):
      raise InvalidArgumentError('order')

    if order.status is Status.Completed.value: #Cant Modify already completed order
      raise OrderAlreadyCompletedError()

    order.status = status.value
    order.save()

  # allow orders to be canceled only if the status is Received
  def cancel_order(self, order):
    if order is None or not isinstance(order, models.Order):
      raise InvalidArgumentError('order')
    
    if order.status != Status.Received.value:
      raise OrderCancellationError()
    
    self.set_status(order, Status.Cancelled)

  # get a list of all orders for a given customer
  def get_all_orders_by_customer(self, customer_id):
    try:
      return self.filter(order_customer_id=customer_id).order_by('status', '-created_at')
    except ValueError:
      raise InvalidArgumentError('customer_id')

  # Get list of incomplete orders for a specific user
  def get_customer_incomplete_orders(self, customer_id):
    try:
      # ~ rep the NOT operator
      return self.filter(~Q(status=Status.Completed.value), order_customer_id=customer_id).order_by('status')
    except:
      raise InvalidArgumentError('customer_id')

  # Get list of all complete orders
  def get_customer_completed_orders(self, customer_id):
    try:
      return self.filter(status=Status.Completed.value, order_customer_id=customer_id)
    except:
      raise InvalidArgumentError('customer_id')

  # Fetch orders at a given status
  def get_orders_by_status(self, status):
    if status is None or not isinstance(status):
      raise InvalidArgumentError('status')

    return self.filter(status=status.value)

  # Get list of orders by a given date range
  def get_orders_by_period(self, start_date, end_date):
    if start_date is None or not isinstance(start_date, datetime):
      raise InvalidArgumentError('start_date')

    if end_date is None or not isinstance(end_date, datetime):
      raise InvalidArgumentError('end_date')

    # created_at__range means that we are going to pass a date range and it will be used as a filter
    result = self.filter(created_at__range=[start_date, end_date])
    return result

  # automatically changes the order to the next status:
  def set_next_status(self, order):
    if order is None or not isinstance(order, models.Order):
      raise InvalidArgumentError('order')
    
    if order.status is Status.Completed.value:
      raise OrderAlreadyCompletedError()
    
    order.status += 1
    order.save()
