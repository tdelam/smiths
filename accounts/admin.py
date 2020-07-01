
from django.contrib import admin

from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
	list_display = ('__unicode__',)
	search_fields = ('email', 'shipping_name', 'contact')
admin.site.register(UserProfile, UserProfileAdmin)