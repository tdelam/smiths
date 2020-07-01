from django.db import models
from django.contrib.auth.models import User

from catalog.models import Product

import datetime

class PageView(models.Model):
    class Meta:
        abstract = True
    
    date = models.DateTimeField(default=datetime.datetime.now)
    ip_address = models.IPAddressField()
    user = models.ForeignKey(User, null=True)
    tracking_id = models.CharField(max_length=50, default='')

class ProductView(PageView):
    product = models.ForeignKey(Product)