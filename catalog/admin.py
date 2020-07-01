from django.contrib import admin

from .models import Product, Category
from .forms import ProductAdminForm


class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('name', 'price', 'old_price', 'is_featured', 'is_active', 'is_bestseller', 'order', 'stock_number')
    list_editable = ('is_featured', 'is_active', 'is_bestseller', 'order', 'stock_number')
    list_filter = ('is_active', 'is_featured')
    list_per_page = 50
    search_fields = ['name', 'description', 'meta_description']
    prepopulated_fields = {'slug' : ('name',)}
admin.site.register(Product, ProductAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at',)
    list_per_page = 20
    ordering = ['name']
    search_fields = ['name', 'description', 'meta_description']
    exclude = ('created_at', 'updated_at',)
    prepopulated_fields = {'slug' : ('name',)}
admin.site.register(Category, CategoryAdmin)
