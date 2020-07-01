import random

from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django.template import RequestContext
from django.core import urlresolvers
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.template import loader, Context
from django.core.mail import EmailMultiAlternatives

from .forms import CheckoutForm
from .models import Order, OrderItem
from . import checkout

from cart import cart
from accounts import profile

from utils import utils

@login_required
def show_checkout(request, template_name='checkout/checkout.html'):
    if cart.is_empty(request):
        cart_url = urlresolvers.reverse('show_cart')
        return redirect(cart_url)
    if request.method == 'POST':
        postdata = request.POST.copy()
        form = CheckoutForm(postdata)
        if form.is_valid():
            response = checkout.process(request) # send credit card info to auth
            order_number = response.get('order_number', 0)
            error_message = response.get('message', '')
            if order_number or request.session.get('pickup', ''):
                request.session['order_number'] = order_number
                request.session['pickupdate'] = postdata['pickdatepick']
                request.session['pickuptime'] = postdata['picktime']
                request.session['location'] = postdata['location']
                if request.session.get('pickup', ''):
                    return redirect(urlresolvers.reverse('checkout_thankyou'))
                else:
                    return redirect(urlresolvers.reverse('checkout_receipt'))
        else:
            error_message = 'Correct the errors below'
    else:
        if request.user.is_authenticated():
            user_profile = profile.retrieve(request)
            form = CheckoutForm(instance=user_profile)
        else:
            form = CheckoutForm()
    page_title = 'Checkout'
    context = RequestContext(request, locals())
    return render_to_response(template_name, context)

@login_required
def receipt(request, template_name='checkout/receipt.html'):
    order_number = request.session.get('order_number', '')
    if order_number:
        order = Order.objects.filter(id=order_number)[0]
        cart_taxes = request.session.get('cart_taxes', 0)
        shipping_price = request.session.get('delivery', 0)

        total = order.total + cart_taxes + shipping_price

        order_items = OrderItem.objects.filter(order=order)
        del request.session['order_number']
        del request.session['cart_taxes']
        del request.session['delivery']
        del request.session['total']
        del request.session['location']
        del request.session['pickupdate']
        del request.session['pickuptime']
        del request.session['pickup']
    else:
        cart_url = urlresolvers.reverse('show_cart')
        return redirect(cart_url)
    context = RequestContext(request, locals())
    return render_to_response(template_name, context)

@login_required
def thanks(request, template_name='checkout/thanks.html'):
    total = request.session.get('total', '')
    location = request.session.get('location', '')
    pickupdate = request.session.get('pickupdate', '')
    pickuptime = request.session.get('pickuptime', '')
    context = RequestContext(request, locals())
    return render_to_response(template_name, context)
