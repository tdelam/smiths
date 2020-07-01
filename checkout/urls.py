from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('checkout.views',
    url(r'^$', 'show_checkout', {'template_name': 'checkout/checkout.html' }, 'checkout'),
    url(r'^thanks/$', 'thanks', {'template_name': 'checkout/thanks.html' },'checkout_thankyou'),
    url(r'^receipt/$', 'receipt', {'template_name': 'checkout/receipt.html' },'checkout_receipt'),
)