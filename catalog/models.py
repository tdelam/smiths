from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, post_delete

from caching.caching import cache_update, cache_evict

from ckeditor.fields import RichTextField

from markdown import markdown

import datetime


class ActiveCategoryManager(models.Manager):
    def get_query_set(self):
        return super(ActiveCategoryManager, self).get_query_set().filter(is_active=True)


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(unique=True, max_length=255)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    meta_description = models.CharField(blank=True, max_length=255)
    created_at = models.DateTimeField(default=datetime.datetime.now)
    updated_at = models.DateTimeField(default=datetime.datetime.now)

    objects = models.Manager()
    active = ActiveCategoryManager()

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "categories"

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('catalog_category', (), { 'category_slug': self.slug })

    @property
    def cache_key(self):
        return self.get_absolute_url()


class ActiveProductManager(models.Manager):
    def get_query_set(self):
        return super(ActiveProductManager, self).get_query_set().filter(is_active=True)


class FeaturedProductManager(models.Manager):
    def all(self):
        return super(FeaturedProductManager, self).all().filter(is_active=True).filter(is_featured=True)


class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, max_length=255)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    tax = models.DecimalField(max_digits=9, decimal_places=2, default=0.13)
    stock_number = models.IntegerField(default=0, null=True, blank=True)
    order = models.IntegerField(default=0, null=True, blank=True)
    old_price = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True, default=0.00)
    plu_number = models.CharField(null=True, blank=True, max_length=50)
    image = models.ImageField(upload_to="product_images", null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    quantity = models.IntegerField(null=True, blank=True, default=1)
    description = RichTextField(null=True, blank=True)
    meta_description = models.CharField(blank=True, max_length=255)
    categories = models.ManyToManyField(Category, null=True, blank=True)

    objects = models.Manager()
    active = ActiveProductManager()
    featured = FeaturedProductManager()

    class Meta:
        ordering = ['-id']

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('catalog_product', (), { 'product_slug': self.slug })

    @property
    def sale_price(self):
        if self.old_price > self.price:
            return self.price
        else:
            return None

    @property
    def cache_key(self):
        return self.get_absolute_url()


    def cross_sells_hybrid(self):
        from checkout.models import Order, OrderItem
        from django.contrib.auth.models import User
        from django.db.models import Q
        orders = Order.objects.filter(orderitem__product=self)
        users = User.objects.filter(order__orderitem__product=self)
        items = OrderItem.objects.filter( Q(order__in=orders) | Q(order__user__in=users)).exclude(product=self)
        products = Product.active.filter(orderitem__in=items).distinct()
        return products

# attach signals to Product and Category model classes
# to update cache data on save and delete operations
post_save.connect(cache_update, sender=Product)
post_delete.connect(cache_evict, sender=Product)
post_save.connect(cache_update, sender=Category)
post_delete.connect(cache_evict, sender=Category)