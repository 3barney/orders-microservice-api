from django.db import models

## Model that stores info about ordering customer 
class OrderCustomer(models.Model):
  customer_id = models.IntegerField()
  name = models.CharField(max_length=100)
  email = models.CharField(max_length=100)


## Model that stores info about customers order
class Order(models.Model):
  ORDER_STATUS = (
    (1, 'Received'),
    (2, 'Processing'),
    (3, 'Payment complete'),
    (4, 'Shipping'),
    (5, 'Completed'),
    (6, 'Cancelled'),
  )

  # define fKey (order_customer) creates Rltnshp between OrderCustomer n Order
  order_customer = models.ForeignKey(OrderCustomer, on_delete=models.CASCADE)
  totals = models.DecimalField(max_digits=9, decimal_places=2, default=0)
  created_at = models.DateTimeField(auto_now_add=True) #auto_now_add, this adds timezone info
  last_updated = models.DateTimeField(auto_now=True)
  status = models.IntegerField(choices=ORDER_STATUS, default='1')

## Holds items belonging to an Order
class OrderItems(models.Model):
  class Meta: #Set metadata information on our Model class
    verbose_name_plural = 'Order Items'

  product_id = models.IntegerField()
  name = models.CharField(max_length=200)
  quantity = models.IntegerField()
  price_per_unit = models.DecimalField(max_digits=9, decimal_places=2, default=0)
  order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
