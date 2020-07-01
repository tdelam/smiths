from django.conf.urls.defaults import *

urlpatterns = patterns('search.views',
    url(r'^results/$','results', {'template_name': 'search/results.html'}, 'search_results'),
)