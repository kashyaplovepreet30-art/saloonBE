from rest_framework import serializers

from products.models import Product
from products.serializers import ProductSerializer

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ("id", "product", "product_id", "quantity", "line_total", "added_at")
        read_only_fields = ("id", "added_at")

    def validate(self, attrs):
        product = attrs.get("product")
        quantity = attrs.get("quantity", getattr(self.instance, "quantity", 1))
        if product and quantity > product.stock_quantity:
            raise serializers.ValidationError(
                {"quantity": "This product is currently out of stock."}
            )
        return attrs


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ("id", "items", "subtotal", "total_items", "updated_at")
        read_only_fields = ("id", "updated_at")
