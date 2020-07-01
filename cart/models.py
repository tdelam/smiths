from django.db import models

from catalog.models import Product

import datetime

class CartItem(models.Model):
    cart_id = models.CharField(max_length=50, db_index=True)
    date_added = models.DateTimeField(default=datetime.datetime.now)
    quantity = models.IntegerField(default=1)
    product = models.ForeignKey(Product, unique=False)
    
    class Meta:
        ordering = ['date_added']
    
    @property
    def total(self):
        return self.quantity * self.product.price
    
    @property
    def name(self):
        return self.product.name
    
    @property
    def price(self):
        return self.product.price
    
    def get_absolute_url(self):
        return self.product.get_absolute_url()
    
    def augment_quantity(self, quantity):
        self.quantity = self.quantity + int(quantity)
        self.save()