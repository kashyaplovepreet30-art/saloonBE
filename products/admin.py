from django.contrib import admin

from .models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "sku",
        "category",
        "price",
        "stock_quantity",
        "status",
        "bestseller",
    )
    list_filter = ("status", "category", "bestseller", "created_at")
    search_fields = ("name", "sku", "brand")
    inlines = [ProductImageInline]
