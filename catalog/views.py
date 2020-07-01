from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.core import urlresolvers
from django.core.cache import cache
from django.conf import settings

from .forms import ProductAddToCartForm
from .models import Category, Product

from cart import cart
from stats import stats


def index(request, template_name='catalog/index.html'):
    page_title = "Home"
    search_recs = stats.recommended_from_search(request)
    featured = Product.featured.all()#[0:settings.PRODUCTS_PER_ROW]
    recently_viewed = stats.get_recently_viewed(request)
    view_recs = stats.recommended_from_views(request)
    context = RequestContext(request, locals())
    return render_to_response(template_name, context)


def show_category(request, category_slug, template_name='catalog/category.html'):
    category_cache_key = request.path
    bestsellers = Product.objects.filter(is_bestseller=True)[:2]
    category = cache.get(category_cache_key)
    if not category:
        # if no cache for category is found, fall back to db query
        category = get_object_or_404(Category, slug=category_slug)
        cache.set(category_cache_key, category, settings.CACHE_TIMEOUT)
    products = category.product_set.filter(is_active=True).order_by('order');
    page_title = category.name
    meta_description = category.meta_description
    context = RequestContext(request, locals())
    return render_to_response(template_name, context)


def show_product(request, product_slug, template_name='catalog/product.html'):
    product = get_object_or_404(Product, slug=product_slug)
    bestsellers = Product.objects.filter(is_bestseller=True)[:2]
    categories = product.categories.filter(is_active=True)
    page_title = product.name
    meta_description = product.meta_description
    if request.method == 'POST':
        postdata = request.POST.copy()
        form = ProductAddToCartForm(request, postdata)
        if form.is_valid():
            cart.add_to_cart(request)
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            url = urlresolvers.reverse('show_cart')
            return redirect(url)
    else:
        form = ProductAddToCartForm(request=request)
    form.fields['product_slug'].widget.attrs['value'] = product_slug
    request.session.set_test_cookie()
    stats.log_product_view(request, product)
    context = RequestContext(request, locals())
    return render_to_response(template_name, context)
