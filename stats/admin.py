from django.contrib import admin

from models import ProductView

class ProductViewAdmin(admin.ModelAdmin):
    list_display = ('product', 'ip_address', 'user')
    list_filter = ('user', 'product')
admin.site.register(ProductView, ProductViewAdmin)