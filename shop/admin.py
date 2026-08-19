from django.contrib import admin
from .models import Category, Product, Store
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "category", "price", "in_stock", "featured")
    list_filter = ("category", "in_stock", "featured")
    search_fields = ("name", "subtitle")
@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "hours", "phone")
