from django.db import models

# Create your models here.


class Category(models.Model):
    type = models.TextField()
   

class Products(models.Model):
    quantity = models.IntegerField()
    name = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)


class SoldItems(models.Model):
    product_name = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.IntegerField()
    sold_date = models.DateTimeField()
    