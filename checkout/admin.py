import random

from django.contrib import admin
from django.core import urlresolvers
from django.shortcuts import redirect

from .models import Order, OrderItem, PostalCodeShipping


class OrderItemInline(admin.StackedInline):
    model = OrderItem
    inline_classes = ('grp-collapse grp-open',)
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'date', 'status', 'transaction_id', 'user')
    list_filter = ('status', 'date')
    search_fields = ('email', 'billing_name', 'id', 'transaction_id')
    inlines = [OrderItemInline,]

    fieldsets = (
        ('Basics', {
            'fields': ('status','email','phone','notes', 'instore_pickup', 'location')
        }),
        ('Billing', {
            'fields': ('billing_name','billing_address_1','billing_address_2',
                'billing_city','billing_state_province','billing_zip_postal','billing_country')
        })
    )
admin.site.register(Order, OrderAdmin)


admin.site.register(PostalCodeShipping)
