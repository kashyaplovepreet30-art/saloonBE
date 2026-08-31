from rest_framework import serializers

from orders.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ("id", "product", "product_name", "quantity", "unit_price", "total_price")
        read_only_fields = ("id",)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source="customer.full_name", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "order_number",
            "customer",
            "customer_name",
            "billing_address",
            "shipping_address",
            "subtotal",
            "discount_amount",
            "tax_amount",
            "total_amount",
            "status",
            "payment_status",
            "coupon_code",
            "items",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "order_number",
            "customer",
            "subtotal",
            "discount_amount",
            "tax_amount",
            "total_amount",
            "created_at",
            "updated_at",
        )


class CheckoutSerializer(serializers.Serializer):
    billing_address = serializers.CharField(required=False, allow_blank=True)
    shipping_address = serializers.CharField()
    coupon_code = serializers.CharField(required=False, allow_blank=True)
    payment_method = serializers.CharField(default="cash")
