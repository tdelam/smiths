import datetime

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.conf import settings

from checkout import checkout

from . import cart


def show_cart(request, template_name='cart/cart.html'):
    error = True
    if request.method == 'POST':
        postdata = request.POST.copy()
        if postdata['submit'] == 'Remove':
            cart.remove_from_cart(request)
        if postdata['submit'] == 'Update':
            cart.update_cart(request)
        if postdata['submit'] == 'Update Total':
            now = datetime.datetime.now()
            datepick = datetime.datetime.strptime(postdata['datepick'], '%m/%d/%Y')
            short_date = '%s/%s/%s' % (now.month, now.day, now.year)
            today = datetime.datetime.strptime(short_date, '%m/%d/%Y')
            is_today = datepick <= today
            if now.hour >= 14 and is_today: # don't allow them to expect delivery today
                error = True
            else:
                error = False
            cart.add_shipping_to_cart(request)
            request.session['datepick'] = postdata['datepick']
            request.session['time'] = postdata['time']
            request.session['postal'] = postdata['postal']
            # Set a session for datepick and time
            # to be used in the saving of order
            #
        if postdata['submit'] == 'Checkout':
            if request.session.get('pickup', ''):
                del request.session['pickup']
            checkout_url = checkout.get_checkout_url(request)
            return redirect(checkout_url)

        if postdata['submit'] == 'Store Pickup':
            if request.session.get('datepick', ''):
                del request.session['datepick']
            if request.session.get('time', ''):
                del request.session['time']
            request.session['pickup'] = True
            checkout_url = checkout.get_checkout_url(request)
            return redirect(checkout_url)

    cart_items = cart.get_cart_items(request)
    page_title = 'Shopping Cart'
    cart_subtotal = cart.cart_subtotal(request)
    cart_taxes = cart.cart_taxes(request)
    postal_code = request.POST.get('postal', 0)
    delivery = cart.add_shipping_to_cart(request)
    request.session['delivery'] = delivery
    total = cart_subtotal + cart_taxes + delivery
    request.session['total'] = total
    request.session['cart_taxes'] = cart.cart_taxes(request)
    context = RequestContext(request, locals())
    return render_to_response(template_name, context)
