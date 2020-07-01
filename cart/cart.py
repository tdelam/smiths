from datetime import datetime, timedelta

import decimal
import random
import json

from django.shortcuts import get_object_or_404, redirect
from django.conf import settings
from django.db.models import Max
from django.http import HttpResponse

from .models import CartItem

from checkout.models import PostalCodeShipping

from catalog.models import Product


CART_ID_SESSION_KEY = 'cart_id'

def _cart_id(request):
    """
    Get the current users cart id or set a new one if none
    """
    if request.session.get(CART_ID_SESSION_KEY, '') == '':
        request.session[CART_ID_SESSION_KEY] = _generate_cart_id()
    return request.session[CART_ID_SESSION_KEY]


def _generate_cart_id():
    """
    Generates a unique cart_id, will be used to fetch the user's cart items
    """
    cart_id = ''
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()'
    cart_id_length = 50
    for y in range(cart_id_length):
        cart_id += characters[random.randint(0, len(characters)-1)]
    return cart_id


def get_cart_items(request):
    """
    Returns all the items from the current user's cart
    """
    return CartItem.objects.filter(cart_id=_cart_id(request))


def add_to_cart(request):
    """
    Add an item to the cart. Get the product to be added by the slug
    and the quantity if exists otherwise the obvious will be '1'.
    If that item is found in the cart augment the quantity.
    The slug comes from a hidden field in the "Add to cart" form.
    """
    postdata = request.POST.copy()
    product_slug = postdata.get('product_slug', '')
    quantity = postdata.get('quantity', 1)
    product = get_object_or_404(Product, slug=product_slug)
    cart_products = get_cart_items(request)
    product_in_cart = False
    for cart_item in cart_products:
        if cart_item.product.id == product.id:
            cart_item.augment_quantity(quantity)
            product_in_cart = True
    if not product_in_cart:
        cart_item = CartItem(product=product, quantity=quantity, cart_id=_cart_id(request))
        cart_item.save()


def cart_distinct_item_count(request):
    """
    Returns the total number of items in the user's cart
    """
    return get_cart_items(request).count()


def get_single_item(request, item_id):
    """
    Returns a CartItem object
    """
    return get_object_or_404(CartItem, id=item_id, cart_id=_cart_id(request))


def update_cart(request):
    """
    Updates the quantity for a single item
    """
    postdata = request.POST.copy()
    item_id = postdata['item_id']
    quantity = postdata['quantity']
    cart_item = get_single_item(request, item_id)
    if cart_item:
        if int(quantity) > 0:
            cart_item.quantity = int(quantity)
            cart_item.save()
        else:
            remove_from_cart(request)


def add_shipping_to_cart(request):
    postdata = request.POST.copy()
    postal_code = postdata.get('postal', '')
    
    shipping_price = 0
    try:
        shipping_price = PostalCodeShipping.objects.get(postal_code=postal_code).price
    except PostalCodeShipping.DoesNotExist:
        pass
    return shipping_price



def remove_from_cart(request):
    """
    Removes a single item from the cart
    """
    postdata = request.POST.copy()
    item_id = postdata['item_id']
    cart_item = get_single_item(request, item_id)
    if cart_item:
        cart_item.delete()


def cart_subtotal(request):
    """
    Gets the total cost for the current cart
    """
    cart_total = decimal.Decimal('0.00')
    cart_products = get_cart_items(request)
    for cart_item in cart_products:
        cart_total += cart_item.product.price * cart_item.quantity
    return cart_total


def cart_taxes(request):
    """
    Taxes
    """
    taxes_total = decimal.Decimal('0.00')
    cart_products = get_cart_items(request)

    for cart_item in cart_products:
        taxes_total += cart_item.product.price * cart_item.quantity * cart_item.product.tax
    return taxes_total


def is_empty(request):
    """
    Returns if empty
    """
    return cart_distinct_item_count(request) == 0


def empty_cart(request):
    """
    Empty the shopping cart
    """
    user_cart = get_cart_items(request)
    user_cart.delete()


def remove_old_cart_items():
    """
    Remove old cart items that are 90 days old, highly unlikely that they will be used anymore
    """
    print "Removing old carts..."
    remove_before = datetime.now() + timedelta(days=-settings.SESSION_AGE_DAYS)
    cart_ids = []
    old_items = CartItem.objects.values('cart_id').annotate(last_change=Max('date_added')).filter(last_change__lt=remove_before).order_by()
    for item in old_items:
        cart_ids.append(item['cart_id'])
    to_remove = CartItem.objects.filter(cart_id__in=cart_ids)
    to_remove.delete()
    print str(len(cart_ids)) + " carts were removed"