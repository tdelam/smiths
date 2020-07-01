from django.db import models
from django.contrib.auth.models import User

from checkout.models import BaseOrderInfo

class UserProfile(BaseOrderInfo):
    user = models.ForeignKey(User, unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_corporate_account = models.BooleanField(default=False)
    
    
    def __unicode__(self):
        return 'User Profile for: %s' % (self.shipping_name)