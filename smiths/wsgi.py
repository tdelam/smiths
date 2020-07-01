"""
WSGI config for myproject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
import sys
import site

site.addsitedir('/srv/virtualenvs/smiths/lib/python2.7/site-packages')
sys.path.append('/srv/virtualenvs/smiths/')
sys.path.append('/srv/virtualenvs/smiths/smiths/')

#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orchards_ecomm.settings")
os.environ["DJANGO_SETTINGS_MODULE"] = "smiths.settings"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
