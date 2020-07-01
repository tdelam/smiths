import urllib
import datetime
import uuid
import logging

from django.core import urlresolvers
from django.conf import settings

from django.http import HttpResponse
from django.template import loader, Context
from django.core.mail import EmailMultiAlternatives

from . import authnet

from .models import Order, OrderItem
from .forms import CheckoutForm

from cart import cart
from accounts import profile


def get_checkout_url(request):
    return urlresolvers.reverse('checkout')

def process(request):
    APPROVED        = '1'
    DECLINED        = '2'
    ERROR           = '3'
    HELD_FOR_REVIEW = '4'

    postdata = request.POST.copy()
    card_num = postdata.get('credit_card_number', '')
    exp_month = postdata.get('credit_card_expire_month', '')
    exp_year = postdata.get('credit_card_expire_year', '')
    exp_date = exp_month + exp_year
    cvv = postdata.get('credit_card_cvv','')
    sub_total = cart.cart_subtotal(request)
    taxes = cart.cart_taxes(request)
    shipping = cart.add_shipping_to_cart(request)
    amount = sub_total + taxes + shipping
    results = {}
    response = []
    is_corp = request.user.userprofile_set.get().is_corporate_account
    is_cod = request.session.get('pickup', '')

    trans_id = str(uuid.uuid4().get_hex().upper()[0:6])
    if not is_corp:
        response = authnet.do_auth_capture(amount=amount, card_num=card_num, exp_date=exp_date, card_cvv=cvv)
    else:
        response.append('1')

    if response[0] == APPROVED and not is_corp or not is_cod:
        transaction_id = response[6]
        order = create_order(request, transaction_id)
        results = {
            'order_number': order.id,
            'message':''
        }
    if response[0] == APPROVED and is_corp or is_cod:
        transaction_id = trans_id
        order = create_order(request, transaction_id)
        results = {
            'order_number': order.id,
            'message':''
        }

    if response[0] == DECLINED:
        results = {
            'order_number': 0,
            'message': 'There is a problem with your credit card.'
        }
    if response[0] == ERROR or response[0] == HELD_FOR_REVIEW:
        results = {
            'order_number': 0,
            'message': 'Error processing your order.'
        }
    return results


def create_order(request, transaction_id):
    order = Order()
    postdata = request.POST.copy()
    checkout_form = CheckoutForm(postdata, instance=order)
    order = checkout_form.save(commit=False)
    order.transaction_id = transaction_id
    order.ip_address = request.META.get('REMOTE_ADDR')
    order.user = None
    if request.user.is_authenticated():
        order.user = request.user
    order.status = Order.SUBMITTED
    order.save()
    if order.pk:
        cart_items = cart.get_cart_items(request)
        for ci in cart_items:
            # create an other item for each cart item
            oi = OrderItem()
            oi.order = order
            oi.delivery_date = request.session.get('datepick', '')
            oi.delivery_time = request.session.get('time', '')
            oi.pickup_date = postdata.get('pickdatepick', '')
            oi.pickup_time = postdata.get('picktime', '')
            oi.quantity = ci.quantity
            oi.price = ci.price # <3 python property decorators
            oi.product = ci.product
            oi.save()
        # empty cart cuz we've ordered
        cart.empty_cart(request)

        # save profile info for future orders
        if request.user.is_authenticated():
            profile.set(request)
    _notify_user(request, order)
    _notify_admin(request, order)
    return order

def _notify_user(request, order):
    html_template = loader.get_template('checkout/email_notification.html')
    plain_template = loader.get_template('checkout/email_notification.txt')

    is_pickup = request.session.get('pickup', False)

    context = Context({
        'order': order,
        'pickupdate': request.session.get('pickupdate', ''),
        'pickuptime': request.session.get('pickuptime', ''),
        'location': request.session.get('location', ''),
        'shipping_price': request.session.get('delivery', ''),
        'overall_total': request.session.get('total', ''),
        'taxes': request.session.get('cart_taxes', ''),
        'is_pickup': is_pickup
    })

    subject, from_email, to = "[Smiths Markets] Order Confirmation", settings.FROM_EMAIL, order.email

    html_content = html_template.render(context)
    plain_content = plain_template.render(context)

    msg = EmailMultiAlternatives(subject, plain_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def _notify_admin(request, order):
    html_template = loader.get_template('checkout/admin_email_notification.html')
    plain_template = loader.get_template('checkout/admin_email_notification.txt')

    is_pickup = request.session.get('pickup', False)

    context = Context({
        'order': order,
        'shipping_price': request.session.get('delivery', ''),
        'pickupdate': request.session.get('pickupdate', ''),
        'pickuptime': request.session.get('pickuptime', ''),
        'location': request.session.get('location', ''),
        'overall_total': request.session.get('total', ''),
        'taxes': request.session.get('cart_taxes', ''),
        'is_pickup': is_pickup
    })
    subject, from_email, to = "[Smiths Markets] New Order!", settings.FROM_EMAIL, settings.ADMIN_EMAIL

    html_content = html_template.render(context)
    plain_content = plain_template.render(context)

    msg = EmailMultiAlternatives(subject, plain_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
