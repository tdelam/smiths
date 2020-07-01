from django.contrib.sites.models import Site

def get_full_path():
    current_site = Site.objects.get_current()    
    full_path = ('https://www.', current_site.domain)
    return ''.join(full_path)