from django import template
from django.core.cache import cache
from django.conf import settings

from cart import cart
from catalog.models import Category

register = template.Library()

@register.inclusion_tag("tags/cart_box.html")
def cart_box(request):
    cart_item_count = cart.cart_distinct_item_count(request)
    return { 'cart_item_count': cart_item_count }

@register.inclusion_tag("tags/categories.html")
def categories(request_path):
    list_cache_key = 'active_category_link_list'
    active_categories = cache.get(list_cache_key)
    if not active_categories:
        active_categories = Category.active.all()
        cache.set(list_cache_key, active_categories, settings.CACHE_TIMEOUT)
    return {
        'active_categories': active_categories,
        'request_path': request_path
        }

@register.inclusion_tag("tags/product_list.html")
def product_list(request, products, header_text):
    return {
        'request': request,
        'products': products,
        'header_text': header_text
        }