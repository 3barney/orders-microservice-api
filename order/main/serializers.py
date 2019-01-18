import functools

from rest_framework import serializers
from .models import Order, OrderCustomer, OrderItems

class OrderCustomerSerializer(serializers.ModelSerializer):
  class Meta:
    model = OrderCustomer
    fields = ('customer_id', 'email', 'name',)


class OrderItemSerializer(serializers.ModelSerializer):
  class Meta:
    model = OrderItems
    fields = ('name', 'price_per_unit', 'product_id', 'quantity', )


class OrderSerializer(serializers.ModelSerializer):
  items = OrderItemSerializer(many=True)
  order_customer=OrderCustomerSerializer()
  status = serializers.SerializerMethodField() #get_status , which will return the display name of the order's status (0,1,2,3,4,5)

  class Meta:
    depth = 1 #depth of the relationships that should be traversed before the serialization
    model = Order
    fields = ('items', 'totals', 'order_customer', 'created_at', 'id', 'status',)
  
  def get_status(self, obj): # method that will get the display value for the ChoiceField status
    return obj.get_status_display()

  # helper method which we are going to use to create and prepare  the order item's objects prior to performing a bulk insert
  # The first argument will be a dictionary with the data about the OrderItem and an order argument with an object of type Order
  def _create_order_item(self, item, order):
    item['order'] = order # update the dictionary passed in the first argument, adding the order object
    return OrderItems(**item)

  # will be called automatically every time we call the serializer's save method:
  def create(self, validated_data):
    validated_customer = validated_data.pop('order_customer')
    validated_items= validated_data.pop('items') # An array of Items

    customer = OrderCustomer.objects.create(**validated_customer) # create customer

    """
      The Order has a foreign key field called order_customer ,
      which is the customer that is connected to that particular Order. What we need to do is
      create a new item in the validated_data dictionary with a key called order_customer ,
    """
    validated_data['order_customer'] = customer
    order = Order.objects.create(**validated_data)

    """
      The map function will apply a function specified as the first argument (partial()) to an iterable ()validated_items 
      that is passed as the second argument, which then returns an iterable with the results.

      The partial function is a high-order function, meaning that it will return another function, it returns
      self._create_order_item and the first argument will be an item of the iterable validated_items.
      The second argument is the order that we created previously.

      value of mapped_items should contain a list of OrderItem objects
    """
    mapped_items = map(functools.partial(self._create_order_item, order=order), validated_items)

    OrderItems.objects.bulk_create(mapped_items)

    return order
  
