from rest_framework import serializers

from .models import Product, ProductImage, ProductStatus


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("id", "image", "alt_text")


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "sku",
            "category",
            "category_name",
            "brand",
            "description",
            "tagline",
            "concern",
            "size",
            "gradient",
            "bestseller",
            "ingredients",
            "details",
            "price",
            "discount",
            "gst_tax",
            "stock_quantity",
            "weight",
            "image",
            "images",
            "status",
            "final_price",
            "in_stock",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        status = attrs.get("status", getattr(self.instance, "status", None))
        stock = attrs.get("stock_quantity", getattr(self.instance, "stock_quantity", 0))
        if status == ProductStatus.OUT_OF_STOCK and stock > 0:
            raise serializers.ValidationError(
                {"status": "Out of stock products cannot have positive stock."}
            )
        return attrs
