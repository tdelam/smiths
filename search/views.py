from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.conf import settings

from . import search


def results(request, template_name='search/results.html'):
    q = request.GET.get('q','')
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    matching = search.products(q).get('products')
    paginator = Paginator(matching, settings.PRODUCTS_PER_PAGE)
    
    try:
        results = paginator.page(page).object_list
    except (InvalidPage, EmptyPage):
        results = paginator.page(1).object_list
    search.store(request, q)
    page_title = "Search results for: %s" % (q)
    context = RequestContext(request, locals())
    return render_to_response(template_name, context)