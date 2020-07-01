import decimal
import datetime

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.template import loader, Context
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.core import urlresolvers
from django.shortcuts import redirect

from catalog.models import Product

from utils import utils


class BaseOrderInfo(models.Model):

    class Meta:
        abstract = True

    email = models.EmailField(max_length=50)
    phone = models.CharField(max_length=20)

    #shipping information
    shipping_name = models.CharField('Name', max_length=50)
    contact = models.CharField(max_length=150, blank=True, null=True)
    shipping_address_1 = models.CharField('Address 1', max_length=50, blank=True, null=True)
    shipping_address_2 = models.CharField('Address 2', max_length=50, blank=True, null=True)

    # billing information
    billing_name = models.CharField(max_length=50, null=True, blank=True)
    billing_address_1 = models.CharField(max_length=50, null=True, blank=True)
    billing_address_2 = models.CharField(max_length=50, null=True, blank=True)
    billing_city = models.CharField(max_length=50, null=True, blank=True)
    billing_state_province = models.CharField(max_length=2, null=True, blank=True)
    billing_country = models.CharField(max_length=50, null=True, blank=True)
    billing_zip_postal = models.CharField(max_length=10, null=True, blank=True)


class Order(BaseOrderInfo):
    SUBMITTED = 1
    PROCESSED = 2
    COMPLETED = 3
    CANCELLED = 4

    ORDER_STATUSES = (
        (SUBMITTED, 'Submitted'),
        (PROCESSED, 'Processed'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    )

    date = models.DateTimeField(default=datetime.datetime.now)
    status = models.IntegerField(choices=ORDER_STATUSES, default=SUBMITTED)
    instore_pickup = models.BooleanField('Pay in Store/C.O.D', default=False)
    location = models.CharField(max_length=100, null=True, blank=True)
    ip_address = models.IPAddressField()
    last_updated = models.DateTimeField(default=datetime.datetime.now)
    user = models.ForeignKey(User, null=True)
    transaction_id = models.CharField(max_length=20)
    notes = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return 'Order # %s' % (str(self.id))

    @property
    def total(self):
        total = decimal.Decimal('0.00')
        order_items = OrderItem.objects.filter(order=self)
        for item in order_items:
            total += item.total
        return total

    @models.permalink
    def get_absolute_url(self):
        return ('order_details', (), { 'order_id': self.id })


class OrderItem(models.Model):

    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7

    WEEKDAYS = (
        (MONDAY, 'Monday'),
        (TUESDAY, 'Tuesday'),
        (WEDNESDAY, 'Wednesday'),
        (THURSDAY, 'Thursday'),
        (FRIDAY, 'Friday'),
        (SATURDAY, 'Saturday'),
        (SUNDAY, 'Sunday'),
    )
    product = models.ForeignKey(Product)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    order = models.ForeignKey(Order)
    delivery_date = models.CharField(max_length=25)
    delivery_time = models.CharField(max_length=25)
    pickup_date = models.CharField(max_length=25, null=True, blank=True)
    pickup_time = models.CharField(max_length=25, null=True, blank=True)


    @property
    def total(self):
        return self.quantity * self.price

    @property
    def name(self):
        return self.product.name

    def __unicode__(self):
        return self.product.name

    def get_absolute_url(self):
        return self.product.get_absolute_url()

class PostalCodeShipping(models.Model):
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)

    def __unicode__(self):
        return ('%s - %s' % (self.postal_code, self.city))

# def notify_admin(sender, instance, **kwargs):
#     html_template = loader.get_template('checkout/email_notification.html')
#     plain_template = loader.get_template('checkout/email_notification.txt')
#
#     context = Context({
#         'instance': instance,
#         'url': utils.get_full_path(),
#     })
#
#     #import pdb; pdb.set_trace()
#     subject, from_email, to = "[ADMIN] New order placed!", settings.FROM_EMAIL, settings.TO_EMAIL
#
#     html_content = html_template.render(context)
#     plain_content = plain_template.render(context)
#
#     msg = EmailMultiAlternatives(subject, plain_content, from_email, [to])
#     msg.attach_alternative(html_content, "text/html")
#     msg.send()
#
# post_save.connect(notify_admin, sender=OrderItem)
