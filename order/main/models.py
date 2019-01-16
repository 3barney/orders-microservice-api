from django.db import models

# Create your models here.
class OrderModels(models.Model):
  customer_id = models.IntegerField()
  name = models.CharField(max_length=100)
  email = models.CharField(max_lenght=100)
