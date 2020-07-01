from .models import SearchTerm

from catalog.models import Product
from stats import stats

from django.db.models import Q

STRIP_WORDS = ['a','an','and','by','for','from','in','no','not',
               'of','on','or','that','the','to','with']

def store(request, q):
    """
    Store the search text in the database
    """
    if len(q) > 1:
        ip = request.META.get('REMOTE_ADDR')
        term = SearchTerm()
        term.q = q
        term.ip_address = ip
        term.user = None
        term.tracking_id = stats.tracking_id(request)
        if request.user.is_authenticated():
            term.user = request.user
        term.save()

def products(search_text):
    """
    Get products matching the search text
    """
    words = _prepare_words(search_text)
    products = Product.active.all()
    results = {}
    results['products'] = []
    for word in words:
        products = products.filter(
            Q(name__icontains=word) |
            Q(description__icontains=word) |
            Q(meta_description__icontains=word)
        ).distinct()
        results['products'] = products
    return results

def _prepare_words(search_text):
    """
    Strip out common words and limit 5 words
    """
    words = search_text.split()
    for common in STRIP_WORDS:
        if common in words:
            words.remove(common)
    return words[0:5]