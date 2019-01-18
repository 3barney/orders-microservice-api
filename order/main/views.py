from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Order
from .serializers import OrderSerializer
from .status import Status
from .view_helper import OrderListApiBaseView
from .view_helper import set_status_handler

# Get orders for a given customer
class OrdersByCustomerView(OrderListApiBaseView):
  # lookup_field will be used to get the value of the keyword argument that is passed
  # on to the kwargs of the list method on the base class.
  lookup_field = 'customer_id'

  """
    calls get_all_orders_by_customer that we created in the Order model manager,
    passing the customer_id .
  """
  def get_queryset(self, customer_id):
    return Order.objects.get_all_orders_by_customer(customer_id)


class IncompleteOrdersByCustomerView(OrderListApiBaseView):
  lookup_field = 'customer_id'

  def get_queryset(self, customer_id):
    return Order.objects.get_customer_incomplete_orders(customer_id)


class CompletedOrdersByCustomerView(OrderListApiBaseView):
  lookup_field = 'customer_id'

  def get_queryset(self, customer_id):
    return Order.objects.get_customer_completed_orders(customer_id)


# List of orders by specific status
class OrderByStatusView(OrderListApiBaseView):
  lookup_field = 'status_id'

  def get_queryset(self, status_id):
    return Order.objects.get_orders_by_status(Status(status_id)) # Status ( status_id ), so we pass the Enum item and not only the ID.


############ POST REquest view

# Base class provides us with post method, 
class CreateOrderView(generics.CreateAPIView):

  def post(self, request, *args, **kwargs):
    serializer = OrderSerializer(data=request.data)

    if serializer.is_valid():
      order = serializer.save()
      return Response({ 'order_id': order.id}, status=status.HTTP_201_CREATED)
    
    return Response(status=status.HTTP_400_BAD_REQUEST)

# get_object_or_404 calls get on a given model

"""
  set_status_handler(); geta another function as an argument, we are passing
  a lambda function that will execute the method in the Order model manager that
  we want
"""
def cancel_order(request, order_id):
  order = get_object_or_404(Order, order_id=order_id)
  return set_status_handler(lambda: Order.objects.cancel_order(order))

def set_next_status(request, order_id):
  order = get_object_or_404(Order, order_id=order_id)
  return set_status_handler(lambda: Order.objects.set_next_status(order))

def set_status(request, order_id, status_id):
  order = get_object_or_404(Order, order_id=order_id)

  try:
    status=Status(status_id)
  except:
    return HttpResponse('The status value is invalid.', status=status.HTTP_400_BAD_REQUEST)
  
  return set_status_handler(lambda: Order.objects.set_status(order, status))


